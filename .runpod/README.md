# Wan 2.2 I2V Remix - Serverless Worker

This worker integrates the Wan 2.2 I2V Remix workflow into RunPod Serverless using a fixed request contract and image-only output.

## Deployment Method: RunPod GitHub + Dockerfile

Use RunPod's GitHub integration to build directly from this repository.

### Steps

1. Push this repository to GitHub.
2. In RunPod, create a new serverless endpoint from GitHub repo.
3. Set build inputs:
   - Context path: `/`
   - Dockerfile path: `Dockerfile`
4. Use H100/H200 class GPU with 1 GPU per worker.
5. Set required env vars:
   - `COMFY_POLLING_MAX_RETRIES=2000`
   - `COMFY_POLLING_INTERVAL_MS=500`
   - `COMFY_HOST=127.0.0.1:8188`
6. Attach network storage if using persistent model volume strategy.
7. Deploy and wait for first build/start completion.

## API Usage

### Request

POST `https://api.runpod.ai/v2/<endpoint_id>/run`

Headers:
- `Authorization: Bearer <RUNPOD_API_KEY>`
- `Content-Type: application/json`

Body:
```json
{
  "input": {
    "start_image": "<BASE64_STRING>",
    "end_image": "<BASE64_STRING>",
    "steps": 8,
    "width": 832,
    "height": 480,
    "model": "high",
    "seed": 12345
  }
}
```

### Response

RunPod wraps handler output. On success, the handler output is:

```json
{
  "image": "<BASE64_IMAGE_STRING>"
}
```

Error behavior:
- `400`: invalid base64 or invalid optional params
- `422`: missing required fields
- `500`: execution/inference failure

## Key Files

- `Dockerfile`
- `handler.py`
- `workflow_runpod.json`
- `runpod.yaml`
