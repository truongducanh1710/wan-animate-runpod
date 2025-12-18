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

# Create symlinks to Network Volume models
# Models will be mounted from Network Volume at /runpod-volume
RUN mkdir -p /comfyui/models && \
    ln -s /runpod-volume/models/diffusion_models /comfyui/models/diffusion_models && \
    ln -s /runpod-volume/models/loras /comfyui/models/loras && \
    ln -s /runpod-volume/models/text_encoders /comfyui/models/text_encodors && \
    ln -s /runpod-volume/models/clip_vision /comfyui/models/clip_vision && \
    ln -s /runpod-volume/models/vae /comfyui/models/vae

# Set environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /

# Start handler
CMD ["python", "-u", "/src/rp_handler.py"]
