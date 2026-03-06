# Wan 2.2 I2V Remix - Implementation Plan

## Goal

Adapt the existing RunPod Serverless worker to support the Wan 2.2 I2V Remix workflow with the required API contract:

- Input: dual base64 images (`start_image`, `end_image`) plus optional generation params.
- Output: single base64 image (`image`) only.
- No video output behavior.
- Production-ready deployment on H100/H200-compatible endpoint configuration.

## Current State Summary

Based on the codebase check:

- Existing handler expects `start_image_base64` / `end_image_base64` and `resolution`, not PRD keys.
- Workflow currently includes video-related nodes (`CreateVideo`, `SaveVideo`, interpolation path).
- Output aggregation can include images/gifs/video and returns `output` instead of `image`.
- Validation and explicit status-code semantics (400/422/500) are incomplete.
- Tests are not currently runnable due to import mismatch and outdated test assumptions.
- Documentation and examples are still aligned to older request/response shapes.

## Implementation Scope

### In Scope

- Update `handler.py` request parsing/validation to PRD schema.
- Update workflow usage to return image-only output from final decode path.
- Add robust base64 validation and clear error classes.
- Map optional params (`model`, `steps`, `width`, `height`, `seed`) to workflow nodes.
- Update docs and request examples for Postman.
- Repair and align tests to new behavior.

### Out of Scope

- Frontend/web app changes.
- New infrastructure architecture.
- Video generation pipeline, interpolation, or MP4 return path.
- Docker redesign beyond minimal required config alignment.

## Work Plan

## Phase 1 - Contract and Validation Layer

1. Update handler input schema:
   - Required: `start_image`, `end_image`
   - Optional: `model`, `steps`, `width`, `height`, `seed`
2. Add strict input checks:
   - Missing required fields -> `422`
   - Invalid base64 -> `400`
   - Invalid type/range values -> `400`
3. Define default values for optional params in one place (constants).
4. Normalize output contract to always return:
   - `{ "image": "<base64>" }` on success.

Deliverable: handler accepts PRD payload and rejects malformed requests deterministically.

## Phase 2 - Workflow Integration (Image-Only)

1. Keep the Wan 2.2 I2V Remix workflow as base template.
2. Remove or bypass video-only nodes from runtime output selection.
3. Ensure final returned artifact comes from image decode output node only.
4. Wire dynamic parameters:
   - `steps` -> sampler step node(s)
   - `width`/`height` -> encode/decode geometry nodes
   - `model` -> selectable model node mapping (explicit allow-list)
   - `seed` -> sampler seed node(s)
5. Keep start/end image injection deterministic via uploaded filenames.

Deliverable: workflow execution returns a single final image (no MP4/gif path).

## Phase 3 - Error Semantics and Runtime Hardening

1. Standardize handler error structure internally:
   - validation error (400/422)
   - execution error (500)
2. Keep detailed server logs while returning safe client error messages.
3. Confirm polling env vars and defaults:
   - `COMFY_POLLING_MAX_RETRIES=2000`
   - `COMFY_POLLING_INTERVAL_MS=500`
4. Add guardrails for empty workflow outputs and missing decode nodes.

Deliverable: predictable failure behavior aligned with PRD response codes.

## Phase 4 - Testing and Verification

1. Fix test import layout so tests run in current repo structure.
2. Add/adjust tests for:
   - valid request (required + defaults)
   - missing `start_image` / `end_image` -> 422
   - invalid base64 -> 400
   - workflow execution failure path -> 500
   - output shape exactly `{ "image": ... }`
3. Add integration test payload samples for Postman and script-based checks.
4. Validate base64 output decodes to a real image file.

Deliverable: runnable test suite and reproducible manual verification path.

## Phase 5 - Documentation and Deployment Alignment

1. Update README request/response examples to PRD format.
2. Update Postman payload files to new contract.
3. Update deployment notes for H100/H200 targeting and env vars.
4. Ensure network storage/model path guidance reflects production setup.

Deliverable: docs are consistent with deployed behavior and QA process.

## Acceptance Checklist

- [ ] Endpoint accepts `start_image` and `end_image` as base64.
- [ ] Optional params (`model`, `steps`, `width`, `height`, `seed`) work with defaults.
- [ ] Invalid base64 returns 400.
- [ ] Missing required fields return 422.
- [ ] Inference/runtime failures return 500.
- [ ] Response payload contains one key: `image` (base64 image).
- [ ] No video artifact returned by API.
- [ ] Postman test succeeds against `/run` endpoint.
- [ ] Output base64 decodes to valid image.
- [ ] Docs and examples match actual implementation.

## Suggested Execution Order

1. Handler schema + validation updates.
2. Workflow output-path correction for image-only.
3. Parameter mapping (`model`, `seed`, geometry) and defaults.
4. Tests fix + new cases.
5. Docs/Postman/deployment notes update.
6. Final end-to-end run on RunPod endpoint.

## Risks and Mitigations

- Workflow node ID drift after JSON edits:
  - Mitigation: centralize node IDs in constants and fail fast if missing.
- Ambiguous `model` mapping:
  - Mitigation: explicit allow-list and default fallback.
- Large output payload size:
  - Mitigation: enforce single-image return only.
- Cold start variance on serverless:
  - Mitigation: use required polling env settings and increased retries.
