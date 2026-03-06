# Deploy and Test on RunPod

## Part 1: Deploy (Serverless from GitHub)

1. **Push this repo to GitHub**  
   Ensure the branch you want to deploy (e.g. `main`) is pushed.

2. **Open RunPod Serverless**  
   - Go to [RunPod Console](https://www.runpod.io/console/serverless)  
   - Or: **Manage → Serverless** in the left sidebar (do **not** use “Pods” / “Deploy a Pod”)

3. **Create endpoint**  
   - Click **New Endpoint** (or **+ New Endpoint**).  
   - Choose **“Start from GitHub Repo”** (or “Connect GitHub”).

4. **Connect repo**  
   - Authorize RunPod with GitHub if asked.  
   - Select this repository and the branch (e.g. `main`).

5. **Build settings**  
   - **Build method:** Dockerfile  
   - **Dockerfile path:** `Dockerfile`  
   - **Context path:** `/` (repo root)

6. **Compute**  
   - **GPU:** H100 SXM (80 GB) — or H100 PCIe if SXM isn’t available.  
   - **GPUs per worker:** 1  
   - **Max workers:** 1–3 as needed.  
   - **Container disk:** 40 GB or more (enough for image + models).

7. **Environment variables**  
   Add (or confirm) these in the endpoint/template:

   | Key | Value |
   |-----|--------|
   | `COMFY_HOST` | `127.0.0.1:8188` |
   | `COMFY_POLLING_MAX_RETRIES` | `2000` |
   | `COMFY_POLLING_INTERVAL_MS` | `500` |

8. **Optional**  
   - Attach a **Network Volume** if you use persistent model storage.  
   - Otherwise the Dockerfile will pull models at build time.

9. **Deploy**  
   - Click **Deploy** / **Create**.  
   - Wait for the first build to finish (can take 10–15+ minutes).  
   - Copy your **Endpoint ID** from the endpoint details (used in the URL below).

---

## Part 2: Test

### Option A: Script (recommended)

From the project root:

```bash
# Replace ENDPOINT_ID and RUNPOD_API_KEY with your values
python3 test_runpod.py YOUR_RUNPOD_API_KEY --url https://api.runpod.ai/v2/ENDPOINT_ID/run --payload postman_example.json
```

- **ENDPOINT_ID:** From RunPod Serverless → your endpoint → ID in the URL or details.  
- **RUNPOD_API_KEY:** RunPod **Account → Settings** (or API Keys) → create/copy key.

On success you’ll see job status and a decoded image saved as `run_output.png` in the current directory.

### Option B: Postman (or any HTTP client)

- **Method:** POST  
- **URL:** `https://api.runpod.ai/v2/<ENDPOINT_ID>/run`  
- **Headers:**
  - `Authorization`: `Bearer <RUNPOD_API_KEY>`
  - `Content-Type`: `application/json`
- **Body (raw JSON):** use the contents of `postman_example.json` (or `test_input.json`).

For **async** runs you get a job `id`; poll:

- **URL:** `https://api.runpod.ai/v2/<ENDPOINT_ID>/status/<JOB_ID>`  
- **Method:** GET  
- **Header:** `Authorization: Bearer <RUNPOD_API_KEY>`

When `status` is `COMPLETED`, the response body has `output.image` (base64). Decode it to verify the image.

### Option C: Synchronous run (wait for result in one call)

- **URL:** `https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync`  
- **Method:** POST  
- **Headers:** same as above.  
- **Body:** same as `postman_example.json`.

Response includes `output.image` when the run succeeds. Use a long timeout (e.g. 300–600 seconds).

---

## Quick checklist

- [ ] Repo pushed to GitHub  
- [ ] Endpoint created from GitHub with Dockerfile at repo root  
- [ ] GPU set to H100 (80 GB)  
- [ ] Env vars set: `COMFY_HOST`, `COMFY_POLLING_MAX_RETRIES`, `COMFY_POLLING_INTERVAL_MS`  
- [ ] First build completed  
- [ ] Endpoint ID and API key copied  
- [ ] Test run with `test_runpod.py` or Postman  
- [ ] `output.image` present and decodes to a valid image
