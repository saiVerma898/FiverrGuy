# Wan 2.2 I2V Remix – Deploy and Test on RunPod (Buyer Guide)

Follow these steps to deploy the serverless endpoint on your RunPod account and test it. No need to share any login details; you do everything in your own RunPod and GitHub.

---

## What You Need

- A **RunPod account** (you must be the **team owner** if using a team, so you can link GitHub).
- The **GitHub repository** with the project code (the developer will push the latest changes; use the repo URL they give you).
- About **15–20 minutes** for the first build (RunPod builds the image and downloads models).

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

## Part 2: Create the Serverless Endpoint from GitHub

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

## Part 3: Configure the Endpoint

1. **Endpoint name**  
   Give it a name, e.g. `wan22-i2v-remix`.

2. **GPU**  
   - **GPU type:** **H100 SXM** (80 GB). If unavailable, choose **H100 PCIe** (80 GB).  
   - **GPUs per worker:** `1`  
   - Do **not** use 24 GB or 48 GB GPUs (e.g. RTX 4090, A40, L40); the workflow needs 80 GB.

3. **Container disk**  
   Set to **40 GB** or higher.

4. **Environment variables**  
   Add these exactly (key = value):

   | Key | Value |
   |-----|--------|
   | `COMFY_HOST` | `127.0.0.1:8188` |
   | `COMFY_POLLING_MAX_RETRIES` | `2000` |
   | `COMFY_POLLING_INTERVAL_MS` | `500` |

5. **Workers**  
   - **Active workers:** `0` (scale to zero when idle) or `1` if you want one always ready.  
   - **Max workers:** `1` or `2` as you prefer.

6. Click **Deploy Endpoint** (or **Create** / **Deploy**).

---

## Part 4: Wait for the Build

1. After deploying, you’ll see the endpoint page and a **Builds** (or similar) section.
2. The first build will:
   - Build the Docker image from the repo.
   - Install custom nodes and download models (~10–15+ minutes).
3. Wait until the build status is **Completed** (or **Success**). If it fails, open the build logs and fix the reported error.
4. When the build is done, the endpoint is ready to receive requests.

---

## Part 5: Get Your Endpoint ID and API Key

1. **Endpoint ID**  
   On the endpoint details page, copy the **Endpoint ID** (from the URL or the endpoint info). It looks like: `xxxxxxxxxxxxxx`.

2. **API key**  
   - Go to **Account** → **Settings** (or [console.runpod.io/user/settings](https://www.console.runpod.io/user/settings)).  
   - Open **API Keys** (or the section where you manage keys).  
   - Create a new key or copy an existing one. You’ll use it as `Bearer YOUR_API_KEY` when calling the API.

Keep both the **Endpoint ID** and the **API key**; you need them to test.

---

## Part 6: Test the Endpoint

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

## Part 7: What Success Looks Like

- **Build:** Build status **Completed** in the RunPod endpoint **Builds** tab.
- **Run:** `POST .../run` returns **200** with a job `id`.
- **Status:** `GET .../status/<id>` eventually returns `"status": "COMPLETED"`.
- **Output:** The response has `"output": { "image": "<base64 string>" }` and no video/MP4. Decoding that base64 gives a single image (PNG).

If you get `"status": "FAILED"`, check the `error` field in the response and the endpoint logs in RunPod for details.

---

## Quick Checklist

- [ ] GitHub connected in RunPod **Settings → Connections**
- [ ] New Serverless endpoint created via **Import GitHub Repository**
- [ ] Repo and branch selected; Dockerfile path = `Dockerfile`, context = `/`
- [ ] GPU = H100 SXM (80 GB), container disk ≥ 40 GB
- [ ] Env vars set: `COMFY_HOST`, `COMFY_POLLING_MAX_RETRIES`, `COMFY_POLLING_INTERVAL_MS`
- [ ] First build completed successfully
- [ ] Endpoint ID and API key copied
- [ ] Test request sent (Postman or curl); job completed with `output.image` present
- [ ] Base64 image decoded and verified

---

## Troubleshooting

- **“Team owner required” when linking GitHub**  
  Only the RunPod account that owns the team can link GitHub. Use that account in **Settings → Connections**.

- **Build fails**  
  Open the build logs in the endpoint’s **Builds** tab. Common issues: wrong Dockerfile path, repo/branch not selected, or network errors during model download.

- **Job stays in queue or fails**  
  Ensure at least one worker can start (e.g. Active workers = 1 or wait for a cold start). Check endpoint logs and the `error` field in the status response.

- **No `image` in output**  
  Confirm you’re using the exact request body above (including `start_image` and `end_image` as base64). The API returns only an image, not video.

If you run into issues, share the RunPod build log or the API error message (redact the API key) so the developer can help.
