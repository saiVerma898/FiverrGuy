import base64
import json
import os
import time
import traceback
import urllib.parse
import uuid
from io import BytesIO

import requests
import runpod
import websocket

COMFY_API_AVAILABLE_INTERVAL_MS = int(os.environ.get("COMFY_POLLING_INTERVAL_MS", 500))
COMFY_API_AVAILABLE_MAX_RETRIES = int(os.environ.get("COMFY_POLLING_MAX_RETRIES", 2000))
COMFY_HOST = os.environ.get("COMFY_HOST", "127.0.0.1:8188")
WORKFLOW_FILE = "workflow_runpod.json"

DEFAULT_STEPS = 8
DEFAULT_WIDTH = 832
DEFAULT_HEIGHT = 480

START_IMAGE_NODE_ID = "148"
ENCODER_NODE_ID = "156"
STEPS_NODE_ID = "150"
MODEL_HIGH_NODE_ID = "131"
MODEL_LOW_NODE_ID = "132"
SAMPLER_A_NODE_ID = "139"
SAMPLER_B_NODE_ID = "140"
DECODE_NODE_ID = "158"
END_IMAGE_NODE_ID = "9001"
SAVE_IMAGE_NODE_ID = "9002"


class APIError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def error_response(status_code, message):
    return {"status_code": status_code, "error": message}


def check_server(url, retries=500, delay=50):
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay / 1000)
    return False


def parse_int(value, key, default=None, minimum=1):
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise APIError(400, f"'{key}' must be an integer")
    if parsed < minimum:
        raise APIError(400, f"'{key}' must be >= {minimum}")
    return parsed


def decode_base64_image(base64_string, key_name):
    if not isinstance(base64_string, str) or not base64_string.strip():
        raise APIError(422, f"Missing required field '{key_name}'")

    normalized = base64_string.strip()
    if "," in normalized:
        normalized = normalized.split(",", 1)[1]

    try:
        return base64.b64decode(normalized, validate=True)
    except Exception as exc:
        raise APIError(400, f"Invalid base64 content in '{key_name}'") from exc


def parse_job_input(job):
    if not isinstance(job, dict):
        raise APIError(422, "Missing job payload")

    job_input = job.get("input")
    if not isinstance(job_input, dict):
        raise APIError(422, "Missing 'input' object")

    normalized_input = {k.strip(): v for k, v in job_input.items()}

    start_image = decode_base64_image(normalized_input.get("start_image"), "start_image")
    end_image = decode_base64_image(normalized_input.get("end_image"), "end_image")

    steps = parse_int(normalized_input.get("steps"), "steps", default=DEFAULT_STEPS)
    width = parse_int(normalized_input.get("width"), "width", default=DEFAULT_WIDTH, minimum=16)
    height = parse_int(normalized_input.get("height"), "height", default=DEFAULT_HEIGHT, minimum=16)
    seed = parse_int(normalized_input.get("seed"), "seed", default=None, minimum=0)

    model = normalized_input.get("model")
    if model is not None and not isinstance(model, str):
        raise APIError(400, "'model' must be a string")
    if isinstance(model, str):
        model = model.strip()
        if model == "":
            model = None

    return {
        "start_image": start_image,
        "end_image": end_image,
        "steps": steps,
        "width": width,
        "height": height,
        "seed": seed,
        "model": model,
    }


def upload_image_bytes(image_bytes, filename):
    files = {"image": (filename, BytesIO(image_bytes), "image/png")}
    data = {"overwrite": "true"}
    response = requests.post(
        f"http://{COMFY_HOST}/upload/image", files=files, data=data, timeout=30
    )
    response.raise_for_status()


def queue_workflow(workflow, client_id):
    payload = {"prompt": workflow, "client_id": client_id}
    response = requests.post(f"http://{COMFY_HOST}/prompt", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def get_history(prompt_id):
    response = requests.get(f"http://{COMFY_HOST}/history/{prompt_id}", timeout=30)
    response.raise_for_status()
    return response.json()


def get_image_data(filename, subfolder, image_type):
    data = {"filename": filename, "subfolder": subfolder, "type": image_type}
    query = urllib.parse.urlencode(data)
    response = requests.get(f"http://{COMFY_HOST}/view?{query}", timeout=60)
    response.raise_for_status()
    return response.content


def wait_until_done(ws, prompt_id, timeout_s=1200):
    start = time.time()
    while True:
        if time.time() - start > timeout_s:
            raise APIError(500, "Workflow execution timed out")

        out = ws.recv()
        if not isinstance(out, str):
            continue

        msg = json.loads(out)
        if msg.get("type") != "executing":
            continue

        data = msg.get("data", {})
        if data.get("node") is None and data.get("prompt_id") == prompt_id:
            return


def load_workflow():
    with open(WORKFLOW_FILE, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    if "input" in json_data and "workflow" in json_data["input"]:
        return json_data["input"]["workflow"]
    return json_data


def apply_model_override(workflow, model_value):
    if not model_value:
        return

    model_key = model_value.strip().lower()
    if model_key == "high":
        workflow[SAMPLER_A_NODE_ID]["inputs"]["model"] = [MODEL_HIGH_NODE_ID, 0]
        workflow[SAMPLER_B_NODE_ID]["inputs"]["model"] = [MODEL_HIGH_NODE_ID, 0]
    elif model_key == "low":
        workflow[SAMPLER_A_NODE_ID]["inputs"]["model"] = [MODEL_LOW_NODE_ID, 0]
        workflow[SAMPLER_B_NODE_ID]["inputs"]["model"] = [MODEL_LOW_NODE_ID, 0]
    else:
        workflow[MODEL_HIGH_NODE_ID]["inputs"]["unet_name"] = model_value
        workflow[MODEL_LOW_NODE_ID]["inputs"]["unet_name"] = model_value


def patch_workflow(workflow, params, start_filename, end_filename):
    required_nodes = [
        START_IMAGE_NODE_ID,
        ENCODER_NODE_ID,
        STEPS_NODE_ID,
        DECODE_NODE_ID,
        SAMPLER_A_NODE_ID,
        SAMPLER_B_NODE_ID,
        MODEL_HIGH_NODE_ID,
        MODEL_LOW_NODE_ID,
    ]
    for node_id in required_nodes:
        if node_id not in workflow:
            raise APIError(500, f"Required workflow node '{node_id}' not found")

    workflow[STEPS_NODE_ID]["inputs"]["value"] = params["steps"]
    workflow[START_IMAGE_NODE_ID]["inputs"]["image"] = start_filename

    workflow[ENCODER_NODE_ID]["inputs"]["start_image"] = [START_IMAGE_NODE_ID, 0]
    workflow[ENCODER_NODE_ID]["inputs"]["end_image"] = [END_IMAGE_NODE_ID, 0]
    workflow[ENCODER_NODE_ID]["inputs"]["width"] = params["width"]
    workflow[ENCODER_NODE_ID]["inputs"]["height"] = params["height"]
    workflow[ENCODER_NODE_ID]["inputs"]["positive_len"] = max(
        params["width"], params["height"]
    )

    workflow[END_IMAGE_NODE_ID] = {
        "inputs": {"image": end_filename, "upload": "image"},
        "class_type": "LoadImage",
    }

    if params["seed"] is not None:
        workflow[SAMPLER_A_NODE_ID]["inputs"]["seed"] = params["seed"]
        workflow[SAMPLER_B_NODE_ID]["inputs"]["seed"] = params["seed"]

    apply_model_override(workflow, params["model"])

    # Force image-only output node and remove video output nodes.
    workflow[SAVE_IMAGE_NODE_ID] = {
        "inputs": {"filename_prefix": "ComfyUI", "images": [DECODE_NODE_ID, 0]},
        "class_type": "SaveImage",
    }
    workflow.pop("115", None)
    workflow.pop("116", None)
    workflow.pop("117", None)

    return workflow


def extract_output_image(prompt_id):
    history = get_history(prompt_id)
    outputs = history.get(prompt_id, {}).get("outputs", {})

    image_entries = []
    save_image_output = outputs.get(SAVE_IMAGE_NODE_ID, {})
    if "images" in save_image_output:
        image_entries = save_image_output["images"]
    else:
        for output in outputs.values():
            if "images" in output:
                image_entries.extend(output["images"])

    if not image_entries:
        raise APIError(500, "No image output generated by workflow")

    first_image = image_entries[0]
    image_bytes = get_image_data(
        first_image["filename"],
        first_image.get("subfolder", ""),
        first_image.get("type", "output"),
    )
    return base64.b64encode(image_bytes).decode("utf-8")


def handler(job):
    ws = None
    try:
        params = parse_job_input(job)

        if not check_server(
            f"http://{COMFY_HOST}/",
            COMFY_API_AVAILABLE_MAX_RETRIES,
            COMFY_API_AVAILABLE_INTERVAL_MS,
        ):
            raise APIError(500, "ComfyUI server unreachable")

        start_filename = f"{uuid.uuid4().hex}_start.png"
        end_filename = f"{uuid.uuid4().hex}_end.png"

        upload_image_bytes(params["start_image"], start_filename)
        upload_image_bytes(params["end_image"], end_filename)

        workflow = load_workflow()
        workflow = patch_workflow(workflow, params, start_filename, end_filename)

        client_id = str(uuid.uuid4())
        ws = websocket.WebSocket()
        ws.connect(f"ws://{COMFY_HOST}/ws?clientId={client_id}", timeout=10)

        queue_response = queue_workflow(workflow, client_id)
        prompt_id = queue_response["prompt_id"]
        wait_until_done(ws, prompt_id)

        image_b64 = extract_output_image(prompt_id)
        return {"image": image_b64}

    except APIError as err:
        return error_response(err.status_code, err.message)
    except Exception as err:
        return error_response(500, f"Execution failed: {err}\n{traceback.format_exc()}")
    finally:
        if ws:
            ws.close()


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
