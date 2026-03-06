# Message to Send to the Buyer (RunPod Team Owner)

Use the text below when asking the buyer to enable GitHub deployment or adjust permissions. Based on [RunPod’s official docs](https://docs.runpod.io/get-started/manage-accounts) and [GitHub integration](https://docs.runpod.io/serverless/github-integration).

---

**Subject:** RunPod deployment – need team owner action for GitHub link

---

Hi,

To deploy the Wan 2.2 I2V Remix serverless endpoint from the repo we’re using, RunPod needs a **GitHub account linked** to your RunPod account. In the RunPod console, when creating a new serverless endpoint, it shows:

**“Team owner required. Only the owner of the team can link a GitHub account.”**

So only the **team owner** (the person who created or owns the RunPod team) can connect GitHub and use “Import GitHub Repository” for deployment.

**Could you do one of the following?**

**Option A – You link GitHub and deploy (simplest)**  
1. In RunPod go to **Account → Settings** → **Connections**: https://www.console.runpod.io/user/settings  
2. Under Connections, click **Connect** for GitHub and authorize RunPod (choose the repo or “All repositories” as you prefer).  
3. Then go to **Manage → Serverless** → **New Endpoint** → **Import GitHub Repository**, select our repo, set Dockerfile path to `Dockerfile`, choose **H100 SXM** (80 GB), add the env vars from the project’s deploy guide, and deploy.  
4. After the first build finishes, share the **Endpoint ID** and an **API key** (from RunPod Settings) so I can run and verify the tests.

**Option B – Give me permissions to link GitHub**  
If RunPod lets you change who can link GitHub:  
1. Go to **Account → Team**: https://www.console.runpod.io/team  
2. Find my user and change my role to **Admin** (or whatever role RunPod allows to “modify team account settings” / link GitHub—see their roles table: https://docs.runpod.io/get-started/manage-accounts#roles-and-permissions).  
3. If linking GitHub is still restricted to “team owner” only, then Option A is the way to go.

Official references:  
- Team roles and permissions: https://docs.runpod.io/get-started/manage-accounts  
- Deploy from GitHub: https://docs.runpod.io/serverless/github-integration  

Once the endpoint is deployed (or I have the right permissions), I’ll run the tests and confirm everything works.

Thanks,  
[Your name]

---

*You can copy the body above and paste it into Fiverr (or your platform) messages. Adjust “our repo” / “the repo” if you refer to it by name or link.*
