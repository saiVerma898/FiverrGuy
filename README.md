# Wan 2.2 I2V Remix - RunPod Serverless Worker

This repository contains the configuration to deploy the **Wan 2.2 I2V Remix** workflow as a Serverless Endpoint on **RunPod**, including required custom nodes and models.

## Deployment Method: GitHub + Dockerfile

We rely on RunPod's **Dockerfile** build system. The repository includes a `Dockerfile` that:
1.  Extends the base ComfyUI image.
2.  Installs the required Custom Nodes (`ComfyUI-WanVideoWrapper`, `comfyui-kjnodes`, etc.).
3.  **Downloads all necessary models** (Wan2.2 Checkpoints, LoRAs, VAE, UMT5) directly into the image.

### Steps to Deploy

1.  **Push this repository to GitHub** (Private or Public).
2.  Go to the [RunPod Console](https://www.runpod.io/console/serverless).
3.  Click **New Endpoint**.
4.  **Connect your GitHub Repository**.
5.  **Build Method**: Select **Dockerfile**.
6.  **GPU Configuration**: Select **H100/H200** class GPUs.
7.  **Environment Variables**:
    - `COMFY_POLLING_MAX_RETRIES`: `2000`
    - `COMFY_POLLING_INTERVAL_MS`: `500`
8.  **Deploy**.
    > **Note**: First build/start can take 10-15 minutes due to model downloads.

---

## API Usage

The worker uses a custom `handler.py`. You do **not** send the full workflow JSON per request.

### Endpoint Input

**POST** to your RunPod Serverless URL (e.g., `https://api.runpod.ai/v2/<endpoint_id>/run`)

**Headers**:
- `Authorization`: `Bearer <YOUR_RUNPOD_KEY>`

**Body**:
```json
{
  "input": {
    "start_image": "<BASE64_STRING_OF_START_IMAGE>",
    "end_image": "<BASE64_STRING_OF_END_IMAGE>",
    "steps": 8,
    "width": 832,
    "height": 480,
    "model": "high",
    "seed": 12345
  }
}
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `start_image` | String | **Required** | Base64 encoded starting image (PNG/JPG). |
| `end_image` | String | **Required** | Base64 encoded ending image (PNG/JPG). |
| `steps` | Integer | `8` | Number of sampling steps. |
| `width` | Integer | `832` | Output width. |
| `height` | Integer | `480` | Output height. |
| `model` | String | workflow default | Optional model selector/override. |
| `seed` | Integer | random workflow behavior | Optional generation seed. |

### Response

The response follows the standard RunPod Serverless format.

```json
{
  "id": "<JOB_ID>",
  "status": "COMPLETED",
  "output": {
    "image": "<BASE64_IMAGE_STRING>"
  }
}
```

If the status is `IN_PROGRESS`, poll the status endpoint (`/status/<JOB_ID>`) until it completes.

### Error Behavior

- `400`: invalid base64 or invalid optional parameter types/ranges.
- `422`: missing required fields.
- `500`: workflow/inference/runtime failures.

---

## Local Development / Files

- **`Dockerfile`**: Defines the build environment and model downloads.
- **`handler.py`**: The Python script that processes requests, updates the workflow, and interacts with ComfyUI.
- **`workflow_runpod.json`**: The base API-format workflow used as a template.
- **`runpod.yaml`**: Configuration file linking the handler.
