#!/bin/bash
# One-time script to populate a RunPod Network Volume with Wan 2.2 I2V models.
# Run this on a Pod that has the volume mounted (default /workspace), or pass the mount path.
# Example: ./populate_volume.sh /workspace
set -e
VOL="${1:-/workspace}"
mkdir -p "$VOL/text_encoders" "$VOL/diffusion_models" "$VOL/loras" "$VOL/vae" "$VOL/frame_interpolation"

download() { curl -fSL -o "$1" "$2"; }

echo "Downloading text encoder..."
download "$VOL/text_encoders/nsfw_wan_umt5-xxl_fp8_scaled.safetensors" \
  "https://huggingface.co/NSFW-API/NSFW-Wan-UMT5-XXL/resolve/main/nsfw_wan_umt5-xxl_fp8_scaled.safetensors"

echo "Downloading diffusion models..."
download "$VOL/diffusion_models/Wan2.2_Remix_NSFW_i2v_14b_low_lighting_v2.0.safetensors" \
  "https://huggingface.co/FX-FeiHou/wan2.2-Remix/resolve/main/NSFW/Wan2.2_Remix_NSFW_i2v_14b_low_lighting_v2.0.safetensors"
download "$VOL/diffusion_models/Wan2.2_Remix_NSFW_i2v_14b_high_lighting_v2.0.safetensors" \
  "https://huggingface.co/FX-FeiHou/wan2.2-Remix/resolve/main/NSFW/Wan2.2_Remix_NSFW_i2v_14b_high_lighting_v2.0.safetensors"

echo "Downloading LoRAs..."
download "$VOL/loras/Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors" \
  "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22-Lightning/old/Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors"
download "$VOL/loras/Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors" \
  "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22-Lightning/old/Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors"

echo "Downloading VAE..."
download "$VOL/vae/wan_2.1_vae.safetensors" \
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"

echo "Downloading frame interpolation model..."
download "$VOL/frame_interpolation/rife47.pth" \
  "https://huggingface.co/wavespeed/misc/resolve/main/rife/rife47.pth"

echo "Done. Volume at $VOL is ready. Attach this volume to your Serverless endpoint and deploy."
