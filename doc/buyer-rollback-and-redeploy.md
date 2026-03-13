# When RunPod Says "Rolled Back" and "Push a New Commit"

## What’s going on

1. **"Endpoint was rolled back to a previous build"**  
   RunPod does this when the **latest** build **failed**. So:
   - The last build (e.g. the one that timed out after 30 minutes) **failed**.
   - RunPod automatically reverted the endpoint to the **previous successful** build.
   - Your endpoint is still running; it’s just using the older image, not the failed one.

2. **"Push a new commit to the branch to start a new build"**  
   RunPod won’t automatically retry the same failed build. To trigger a **new** build, something on the branch must change — i.e. **push a new commit** to that branch (e.g. `main`). That starts a fresh build from scratch.

3. **Why the build failed (from the logs)**  
   - **Build exceeded maximum time limit of 1800 seconds (30.0 minutes).**  
     The image was too big (or the export/upload took too long), so the build was stopped after 30 minutes.
   - **WARNING: git was not found in the system**  
     The RunPod build environment doesn’t have `git` in `$PATH`. That’s a RunPod quirk and is usually not the main cause of the timeout.

## What to do so the next build succeeds

- Use the **Network Volume** setup: the Dockerfile in the repo **no longer** downloads models into the image, so the image is much smaller and the build should finish in **~10–15 minutes** (under the 30‑min limit).
- Make sure that version of the repo is what RunPod is building:
  1. **Push the latest code** (the commit with Network Volume: no model downloads in Dockerfile, `entrypoint.sh`, `scripts/populate_volume.sh`) to the branch RunPod is watching (e.g. `main`).
  2. That push **is** the “new commit” RunPod asked for — it will start a new build.
  3. Before that build can be useful, the buyer must **create a Network Volume, populate it** with `scripts/populate_volume.sh`, and **attach it** to the endpoint (see **doc/buyer-deploy-and-test-guide.md**). Otherwise the new image will start but have no models.

## Short message you can send the buyer

Copy and adapt:

---

**Rollback / redeploy**

RunPod rolled back because the last build **timed out** (over 30 minutes). The endpoint is still up; it’s just running the previous image.

To start a **new** build, push a new commit to the branch (e.g. `main`). I’ve pushed the latest code that uses a Network Volume so the image is smaller and the build should finish in ~10–15 minutes.

Please:

1. Pull the latest from the repo (or confirm you’re on the latest commit).
2. Create a Network Volume, populate it once with `scripts/populate_volume.sh` (see **doc/buyer-deploy-and-test-guide.md**), and attach that volume to the endpoint.
3. Push any small change to `main` (or the branch RunPod uses) to trigger a new build — e.g. an empty commit:  
   `git commit --allow-empty -m "Trigger rebuild" && git push origin main`

After the new build completes, the endpoint will use the new image and the volume for models. If the build still fails, send me the build log and I’ll help debug.

---
