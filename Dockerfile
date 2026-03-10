# clean base image containing only comfyui, comfy-cli and comfyui-manager
FROM runpod/worker-comfyui:5.5.1-base

# install custom nodes into comfyui
RUN comfy node install --exit-on-fail ComfyUI-WanVideoWrapper@1.4.5 --mode remote
RUN comfy node install --exit-on-fail comfyui-wanvideowrapper@1.4.5
RUN comfy node install --exit-on-fail comfyui-kjnodes@1.2.8
RUN comfy node install --exit-on-fail comfyui-frame-interpolation@1.0.7
RUN comfy node install --exit-on-fail comfyui-custom-scripts@1.2.5
RUN comfy node install --exit-on-fail comfyui-easy-use@1.3.6

# Models are loaded from a RunPod Network Volume at /runpod-volume (see entrypoint.sh).
# Populate the volume once using scripts/populate_volume.sh on a Pod or via S3.

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

COPY . .