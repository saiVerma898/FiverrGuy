import base64
import sys
import types
import unittest
from unittest.mock import patch

# Lightweight stubs so unit tests run without full runtime deps installed locally.
if "requests" not in sys.modules:
    sys.modules["requests"] = types.SimpleNamespace(get=None, post=None)
if "runpod" not in sys.modules:
    sys.modules["runpod"] = types.SimpleNamespace(
        serverless=types.SimpleNamespace(start=lambda *_args, **_kwargs: None)
    )
if "websocket" not in sys.modules:
    sys.modules["websocket"] = types.SimpleNamespace(WebSocket=object)

import handler


TEST_IMAGE_B64 = base64.b64encode(b"fake-image-bytes").decode("utf-8")


class TestWan22Handler(unittest.TestCase):
    def test_parse_job_input_missing_job(self):
        with self.assertRaises(handler.APIError) as context:
            handler.parse_job_input(None)
        self.assertEqual(context.exception.status_code, 422)

    def test_parse_job_input_defaults(self):
        job = {"input": {"start_image": TEST_IMAGE_B64, "end_image": TEST_IMAGE_B64}}
        parsed = handler.parse_job_input(job)
        self.assertEqual(parsed["steps"], 8)
        self.assertEqual(parsed["width"], 832)
        self.assertEqual(parsed["height"], 480)
        self.assertIsNone(parsed["seed"])
        self.assertIsNone(parsed["model"])

    def test_parse_job_input_missing_required(self):
        with self.assertRaises(handler.APIError) as context:
            handler.parse_job_input({"input": {"start_image": TEST_IMAGE_B64}})
        self.assertEqual(context.exception.status_code, 422)

    def test_parse_job_input_invalid_base64(self):
        with self.assertRaises(handler.APIError) as context:
            handler.parse_job_input(
                {"input": {"start_image": "not-valid", "end_image": TEST_IMAGE_B64}}
            )
        self.assertEqual(context.exception.status_code, 400)

    @patch("handler.check_server", return_value=False)
    def test_handler_server_unreachable(self, _mock_check):
        result = handler.handler(
            {"input": {"start_image": TEST_IMAGE_B64, "end_image": TEST_IMAGE_B64}}
        )
        self.assertEqual(result["status_code"], 500)
        self.assertIn("ComfyUI server unreachable", result["error"])

    def test_patch_workflow_sets_image_only_output(self):
        workflow = {
            "131": {"inputs": {"unet_name": "high.safetensors"}},
            "132": {"inputs": {"unet_name": "low.safetensors"}},
            "139": {"inputs": {"model": ["131", 0]}},
            "140": {"inputs": {"model": ["132", 0]}},
            "148": {"inputs": {"image": "old.png"}},
            "150": {"inputs": {"value": 4}},
            "156": {"inputs": {"width": 640, "height": 360, "positive_len": 640}},
            "158": {"inputs": {}},
            "115": {"inputs": {}},
            "116": {"inputs": {}},
            "117": {"inputs": {}},
        }
        params = {
            "steps": 8,
            "width": 832,
            "height": 480,
            "seed": 7,
            "model": "high",
        }
        patched = handler.patch_workflow(
            workflow, params, "start_file.png", "end_file.png"
        )

        self.assertIn("9002", patched)
        self.assertEqual(patched["9002"]["class_type"], "SaveImage")
        self.assertNotIn("115", patched)
        self.assertNotIn("116", patched)
        self.assertNotIn("117", patched)


if __name__ == "__main__":
    unittest.main()
