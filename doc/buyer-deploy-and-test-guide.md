# Wan 2.2 I2V Remix – Deploy and Test on RunPod (Buyer Guide)

Follow these steps to deploy the serverless endpoint on your RunPod account and test it. No need to share any login details; you do everything in your own RunPod and GitHub.

Models are stored on a **RunPod Network Volume** so the Docker image stays small and the build finishes within the 30‑minute limit. You create the volume once, populate it with the model files (one-time), then attach it to the endpoint.

---

## What You Need

- A **RunPod account** (you must be the **team owner** if using a team, so you can link GitHub).
- The **GitHub repository** with the project code (the developer will push the latest changes; use the repo URL they give you).
- About **10–15 minutes** for the first build (no model download in the image).
- One-time setup: create a **Network Volume** and run the populate script (~30–60 min download on a temporary Pod).

---

## Part 1: Link GitHub to RunPod

1. Log in to RunPod: [console.runpod.io](https://www.console.runpod.io)
2. Go to **Account** (left sidebar) → **Settings** (or open [console.runpod.io/user/settings](https://www.console.runpod.io/user/settings)).
3. Find the **Connections** section.
4. Click **Connect** next to **GitHub**.
5. In the GitHub authorization screen:
   - Sign in to GitHub if needed.
   - Choose **Only select repositories** and pick the repo that contains the project, **or** choose **All repositories** if you prefer.
   - Authorize RunPod.
6. Return to RunPod and confirm GitHub shows as connected. You only need to do this once.

---

## Part 2: Create and Populate the Network Volume (one-time)

Models are loaded from a RunPod Network Volume so the image build stays under the 30‑minute limit. Do this once; then attach the same volume to your Serverless endpoint.

### 2.1 Create the volume

1. In RunPod go to **Storage** (or [console.runpod.io/user/storage](https://www.console.runpod.io/user/storage)).
2. Click **Create Network Volume** (or **New Network Volume**).
3. Set **Size** to **50 GB** or more (models need ~30 GB).
4. Choose a **datacenter** (e.g. same as you’ll use for the endpoint; e.g. **US-KS-2**).
5. Name it (e.g. `wan22-models`) and create the volume.

### 2.2 Populate the volume using a temporary Pod

1. Go to **Pods** → **Deploy** (or **+ Deploy**).
2. Deploy a **Pod** (not Serverless) with:
   - **GPU:** any (e.g. 1× RTX 4090 or CPU-only if available).
   - **Template:** e.g. **RunPod Pytorch** or any image with `curl` and bash.
   - **Network Volume:** attach the volume you created; mount path **/workspace** (default).
3. Once the Pod is running, open **Connect** → **Web Terminal** (or SSH).
4. Download and run the populate script (from the repo). If you have the repo locally, you can copy `scripts/populate_volume.sh` into the Pod, or run the commands manually. Easiest: clone the repo on the Pod and run the script:

   ```bash
   apt-get update && apt-get install -y curl git
   git clone https://github.com/YOUR_ORG/YOUR_REPO.git /tmp/repo
   chmod +x /tmp/repo/scripts/populate_volume.sh
   /tmp/repo/scripts/populate_volume.sh /workspace
   ```

   Replace `YOUR_ORG/YOUR_REPO` with the actual GitHub repo. The script downloads all required models into `/workspace` (your volume). This can take **30–60 minutes** depending on network speed.
5. When the script finishes, **stop/terminate the Pod**. The volume keeps the data. You can delete the Pod; the volume is independent.

### 2.3 (Optional) Using RunPod’s S3-compatible API

If your volume is in a [supported datacenter](https://docs.runpod.io/serverless/storage/network-volumes#s3-compatible-api) (e.g. **US-KS-2**, **EU-RO-1**), you can upload the model files via the S3 API instead of using a Pod. See RunPod’s [S3 API docs](https://docs.runpod.io/storage/s3-api). The volume must contain these top-level folders with the correct filenames: `text_encoders/`, `diffusion_models/`, `loras/`, `vae/`, `frame_interpolation/` (same layout as produced by `populate_volume.sh`).

---

## Part 3: Create the Serverless Endpoint from GitHub

1. In the left sidebar go to **Manage** → **Serverless** (do **not** use “Pods” or “Deploy a Pod”).
2. Click **New Endpoint** (or **+ New Endpoint**).
3. Choose **Import GitHub Repository** (or “Start from GitHub Repo”).
4. In the repository dropdown, select the **Wan 2.2 I2V Remix** project repo (the one the developer pushed).
5. Set:
   - **Branch:** e.g. `main` (or the branch the developer tells you).
   - **Dockerfile path:** `Dockerfile`
   - **Context path:** `/` (repo root)
6. Click **Next** (or continue to endpoint configuration).

---

## Part 4: Configure the Endpoint

1. **Endpoint name**  
   Give it a name, e.g. `wan22-i2v-remix`.

2. **GPU**  
   - **GPU type:** **H100 SXM** (80 GB). If unavailable, choose **H100 PCIe** (80 GB).  
   - **GPUs per worker:** `1`  
   - Do **not** use 24 GB or 48 GB GPUs (e.g. RTX 4090, A40, L40); the workflow needs 80 GB.

3. **Container disk**  
   Set to **40 GB** or higher.

4. **Network Volume**  
   Expand **Advanced** (or scroll to **Network Volumes**). Attach the **same** Network Volume you created and populated in Part 2. Workers will see it at `/runpod-volume`; the image uses it automatically for models.

5. **Environment variables**  
   Add these exactly (key = value):

   | Key | Value |
   |-----|--------|
   | `COMFY_HOST` | `127.0.0.1:8188` |
   | `COMFY_POLLING_MAX_RETRIES` | `2000` |
   | `COMFY_POLLING_INTERVAL_MS` | `500` |

6. **Workers**  
   - **Active workers:** `0` (scale to zero when idle) or `1` if you want one always ready.  
   - **Max workers:** `1` or `2` as you prefer.

7. Click **Deploy Endpoint** (or **Create** / **Deploy**).

---

## Part 5: Wait for the Build

1. After deploying, you’ll see the endpoint page and a **Builds** (or similar) section.
2. The build only installs custom nodes and app code (no model download in the image), so it should finish in **about 10–15 minutes** and stay within the 30‑minute build limit.
3. Wait until the build status is **Completed** (or **Success**). If it fails, open the build logs and fix the reported error.
4. When the build is done, the endpoint is ready. Workers will load models from the attached Network Volume at startup.

---

## Part 6: Get Your Endpoint ID and API Key

1. **Endpoint ID**  
   On the endpoint details page, copy the **Endpoint ID** (from the URL or the endpoint info). It looks like: `xxxxxxxxxxxxxx`.

2. **API key**  
   - Go to **Account** → **Settings** (or [console.runpod.io/user/settings](https://www.console.runpod.io/user/settings)).  
   - Open **API Keys** (or the section where you manage keys).  
   - Create a new key or copy an existing one. You’ll use it as `Bearer YOUR_API_KEY` when calling the API.

Keep both the **Endpoint ID** and the **API key**; you need them to test.

---

## Part 7: Test the Endpoint

You can test with **Postman** (or any HTTP client) or with **curl**. The API returns a job ID first; you then poll for the result.

### Option A: Postman (or Insomnia / similar)

**Step 1 – Start a job**

- **Method:** `POST`
- **URL:** `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run`  
  Replace `YOUR_ENDPOINT_ID` with your actual Endpoint ID.
- **Headers:**
  - `Authorization`: `Bearer YOUR_API_KEY`
  - `Content-Type`: `application/json`
- **Body:** raw JSON. Use this exactly (it’s a minimal valid request with tiny test images):

```json
{
  "input": {
    "start_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
    "end_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
    "steps": 8,
    "width": 832,
    "height": 480,
    "model": "high",
    "seed": 12345
  }
}
```

Send the request. You should get a **200** response with a JSON body containing an `"id"` (job ID). Copy that `id`.

**Step 2 – Get the result**

- **Method:** `GET`
- **URL:** `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/JOB_ID`  
  Replace `YOUR_ENDPOINT_ID` with your Endpoint ID and `JOB_ID` with the `id` from Step 1.
- **Header:** `Authorization`: `Bearer YOUR_API_KEY`

Send the request. Repeat every 10–20 seconds until:

- `"status": "COMPLETED"` → success. The body will contain `"output": { "image": "<base64 string>" }`.
- `"status": "FAILED"` → check the `"error"` field in the response.

**Step 3 – Verify the image**

- When `status` is `COMPLETED`, copy the long string inside `output.image`.
- Use any base64-to-image tool (e.g. [base64.guru](https://base64.guru/convert/decode/image) or a small script) to decode it. You should get a single image (PNG). That confirms the endpoint is working.

---

### Option B: curl (command line)

**Step 1 – Start a job**

Run this in a terminal (replace `YOUR_ENDPOINT_ID` and `YOUR_API_KEY`):

```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":{"start_image":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=","end_image":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=","steps":8,"width":832,"height":480,"model":"high","seed":12345}}'
```

From the response JSON, copy the `"id"` value (job ID).

**Step 2 – Poll for result**

Replace `JOB_ID` and run:

```bash
curl -X GET "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/JOB_ID" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Repeat until `"status"` is `"COMPLETED"` or `"FAILED"`. When `COMPLETED`, `output.image` contains the base64 image.

---

### Option C: If you have the project repo on your machine (Python script)

If you have cloned the repo and have Python 3 and `requests` installed:

```bash
cd path/to/repo
python3 test_runpod.py YOUR_API_KEY --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run --payload postman_example.json
```

Replace `YOUR_API_KEY` and `YOUR_ENDPOINT_ID`. On success, the script saves the output image as `run_output.png` in the current folder.

---

## Part 8: What Success Looks Like

- **Build:** Build status **Completed** in the RunPod endpoint **Builds** tab.
- **Run:** `POST .../run` returns **200** with a job `id`.
- **Status:** `GET .../status/<id>` eventually returns `"status": "COMPLETED"`.
- **Output:** The response has `"output": { "image": "<base64 string>" }` and no video/MP4. Decoding that base64 gives a single image (PNG).

If you get `"status": "FAILED"`, check the `error` field in the response and the endpoint logs in RunPod for details.

---

## Quick Checklist

- [ ] GitHub connected in RunPod **Settings → Connections**
- [ ] **Network Volume** created (≥50 GB) and **populated** with `scripts/populate_volume.sh` on a temporary Pod
- [ ] New Serverless endpoint created via **Import GitHub Repository**
- [ ] **Network Volume attached** to the endpoint (Advanced → Network Volumes)
- [ ] Repo and branch selected; Dockerfile path = `Dockerfile`, context = `/`
- [ ] GPU = H100 SXM (80 GB), container disk ≥ 40 GB
- [ ] Env vars set: `COMFY_HOST`, `COMFY_POLLING_MAX_RETRIES`, `COMFY_POLLING_INTERVAL_MS`
- [ ] First build completed successfully (within ~10–15 min)
- [ ] Endpoint ID and API key copied
- [ ] Test request sent (Postman or curl); job completed with `output.image` present
- [ ] Base64 image decoded and verified

---

## Troubleshooting

- **Build exceeds 30 minutes**  
  With the current setup, models are **not** in the image; they are loaded from the attached Network Volume. The build should finish in ~10–15 min. If you still hit a timeout, ensure the Network Volume is attached and populated so you're using this repo's Dockerfile (no model download steps).

- **Worker fails or "models not found"**  
  Ensure the Network Volume is **attached** to the endpoint and was **populated** with `scripts/populate_volume.sh` (or the same folder layout: `text_encoders/`, `diffusion_models/`, `loras/`, `vae/`, `frame_interpolation/`). The volume is mounted at `/runpod-volume`.

- **“Team owner required” when linking GitHub**  
  Only the RunPod account that owns the team can link GitHub. Use that account in **Settings → Connections**.

- **Build fails**  
  Open the build logs in the endpoint’s **Builds** tab. Common issues: wrong Dockerfile path, repo/branch not selected, or network errors during custom node install.

- **Job stays in queue or fails**  
  Ensure at least one worker can start (e.g. Active workers = 1 or wait for a cold start). Check endpoint logs and the `error` field in the status response.

- **No `image` in output**  
  Confirm you’re using the exact request body above (including `start_image` and `end_image` as base64). The API returns only an image, not video.

If you run into issues, share the RunPod build log or the API error message (redact the API key) so the developer can help.
