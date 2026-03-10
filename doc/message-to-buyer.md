# Message to Send to the Buyer (After Repo Update – Network Volume)

Use the text below when sending the buyer the updated repo and deployment steps.

---

**Subject:** Repo updated – here’s how to deploy and test (Network Volume setup)

---

Hello my friend,

I’ve updated the repo to fix the build timeout issue. The build was failing because the image was too large and hit the 30‑minute limit. Models are now loaded from a **RunPod Network Volume** instead of being baked into the image, so the build finishes in about 10–15 minutes and stays under the limit.

**Here’s what you need to do to test:**

1. **Pull the latest code** from the repo (main branch or the branch I told you).

2. **Create and populate a Network Volume (one-time):**
   - In RunPod go to **Storage** → **Create Network Volume** (50 GB or more, pick a datacenter like US-KS-2).
   - Deploy a **temporary Pod** (Pods → Deploy) with that volume attached at `/workspace`, any GPU or CPU template.
   - In the Pod’s terminal run:
     ```bash
     apt-get update && apt-get install -y curl git
     git clone https://github.com/YOUR_ORG/YOUR_REPO.git /tmp/repo
     chmod +x /tmp/repo/scripts/populate_volume.sh
     /tmp/repo/scripts/populate_volume.sh /workspace
     ```
     (Replace YOUR_ORG/YOUR_REPO with the actual repo URL.)  
     This downloads all models onto the volume and can take 30–60 minutes. When it’s done, you can stop/delete the Pod; the volume keeps the data.

3. **Create the Serverless endpoint** (or use an existing one):
   - **Manage** → **Serverless** → **New Endpoint** → **Import GitHub Repository**, select the repo, branch, Dockerfile path `Dockerfile`.
   - In **Advanced**, attach the **same Network Volume** you just populated.
   - Set GPU to **H100 SXM** (80 GB), container disk ≥ 40 GB, and add env vars: `COMFY_HOST=127.0.0.1:8188`, `COMFY_POLLING_MAX_RETRIES=2000`, `COMFY_POLLING_INTERVAL_MS=500`.
   - Deploy. The build should complete in ~10–15 min.

4. **Test the endpoint** with Postman or curl (see the guide in the repo). Send a `POST` to `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run` with your API key and a JSON body with `start_image` and `end_image` (base64), then poll `.../status/JOB_ID` until you get `output.image`.

All the details (including the exact request body and checklist) are in the repo: **doc/buyer-deploy-and-test-guide.md**. If anything is unclear or you hit an error, send me the build log or the API response (with the API key redacted) and I’ll help you fix it.

Thanks,  
[Your name]

---

*You can copy the body above and paste it into Fiverr (or your platform) messages. Replace YOUR_ORG/YOUR_REPO and [Your name] as needed.*
