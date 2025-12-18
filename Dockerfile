FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel

# Set working directory
WORKDIR /comfyui

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui
WORKDIR /comfyui

# Install ComfyUI dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install custom nodes
WORKDIR /comfyui/custom_nodes

# 1. ControlNet Aux
RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
    cd comfyui_controlnet_aux && \
    pip install --no-cache-dir -r requirements.txt

# 2. KJNodes
RUN git clone https://github.com/kijai/ComfyUI-KJNodes.git && \
    cd ComfyUI-KJNodes && \
    pip install --no-cache-dir -r requirements.txt

# 3. SAM2
RUN git clone https://github.com/kijai/ComfyUI-segment-anything-2.git && \
    cd ComfyUI-segment-anything-2 && \
    pip install --no-cache-dir -r requirements.txt

# Install RunPod handler dependencies
COPY builder/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy handler code and workflow
COPY src /src
COPY workflows /workflows

# Create model directories
RUN mkdir -p /comfyui/models/diffusion_models && \
    mkdir -p /comfyui/models/loras && \
    mkdir -p /comfyui/models/text_encoders && \
    mkdir -p /comfyui/models/clip_vision && \
    mkdir -p /comfyui/models/vae

# Download models during build
WORKDIR /comfyui/models

# Download Diffusion Model (18GB)
RUN wget -q --show-progress -O diffusion_models/Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors \
    https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/Wan22Animate/Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors

# Download LoRAs
RUN wget -q --show-progress -O loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors \
    https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors && \
    wget -q --show-progress -O loras/WanAnimate_relight_lora_fp16.safetensors \
    https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Wan22_relight/WanAnimate_relight_lora_fp16.safetensors

# Download Text Encoder (6.3GB)
RUN wget -q --show-progress -O text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors \
    https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors

# Download CLIP Vision
RUN wget -q --show-progress -O clip_vision/clip_vision_h.safetensors \
    https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors

# Download VAE
RUN wget -q --show-progress -O vae/wan_2.1_vae.safetensors \
    https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors

# Set environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /

# Start handler
CMD ["python", "-u", "/src/rp_handler.py"]
