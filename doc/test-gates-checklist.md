# Test Gates Checklist

Use this sequence to validate the project without wasting time on heavy installs too early.

## Gate 1 - Local Contract and Unit Validation

Purpose: verify API contract and handler logic before container/deployment work.

- [ ] Install Stage 1 dependencies:
  - `python3 -m pip install -r requirements.txt`
- [ ] Run local tests:
  - `python3 -m unittest discover -s tests -q`
- [ ] Validate request schema support:
  - required: `start_image`, `end_image`
  - optional: `model`, `steps`, `width`, `height`, `seed`
- [ ] Validate error behavior:
  - missing fields -> 422
  - invalid base64 -> 400
  - runtime failure path -> 500
- [ ] Confirm output shape is image-only:
  - `{ "image": "<base64>" }`

Exit criteria: local tests pass and contract behavior is stable.

## Gate 2 - Container Build and Runtime Sanity

Purpose: verify Docker/runtime composition before full endpoint rollout.

- [ ] Build image:
  - `docker build --platform linux/amd64 -t wan22-i2v-worker .`
- [ ] Confirm custom nodes install during build logs.
- [ ] Confirm model downloads complete (or are mounted via network volume strategy).
- [ ] Confirm runtime env defaults:
  - `COMFY_POLLING_MAX_RETRIES=2000`
  - `COMFY_POLLING_INTERVAL_MS=500`
  - `COMFY_HOST=127.0.0.1:8188`
- [ ] Smoke run container and ensure handler starts without import/runtime errors.

Exit criteria: image builds cleanly and worker boots with expected environment.

## Gate 3 - RunPod End-to-End Validation

Purpose: production-like inference verification.

- [ ] Deploy/update endpoint on H100/H200 class GPU target.
- [ ] Attach network storage / model volume as needed.
- [ ] Configure required env vars in endpoint.
- [ ] Run Postman request against:
  - `POST https://api.runpod.ai/v2/<endpoint-id>/run`
- [ ] Validate successful response contains image payload.
- [ ] Decode returned base64 and verify it is a valid image file.
- [ ] Verify parameter behavior changes output (`steps`, `width`, `height`, `model`, `seed`).

Exit criteria: reproducible successful E2E call with valid image output.
