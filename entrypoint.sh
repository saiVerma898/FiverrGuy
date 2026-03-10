#!/bin/bash
set -e
# When a RunPod Network Volume is attached, it is mounted at /runpod-volume.
# We expect it to contain the ComfyUI models layout: text_encoders/, diffusion_models/, loras/, vae/, frame_interpolation/
if [ -d /runpod-volume/diffusion_models ] && [ -n "$(ls -A /runpod-volume/diffusion_models 2>/dev/null)" ]; then
  rm -rf /comfyui/models
  ln -sf /runpod-volume /comfyui/models
fi
exec "$@"
