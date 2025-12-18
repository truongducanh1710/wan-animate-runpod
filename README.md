# Wan2.2 Animate 14B - RunPod Serverless Endpoint

Deploy ComfyUI với Wan2.2 Animate 14B model lên RunPod Serverless để tạo video AI chất lượng cao.

## 🎯 Tính năng

- **Character Animation**: Thay thế nhân vật trong video với AI
- **Pose Transfer**: Chuyển động tư thế từ video gốc sang nhân vật mới
- **Mix Mode**: Kết hợp background và character mask
- **High Quality**: Sử dụng model 14B parameters cho chất lượng tốt nhất

## 📋 Yêu cầu

### Models (đã có trong Network Volume)

Tất cả models đã được download vào Network Volume:

```
/workspace/models/
├── diffusion_models/
│   └── Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors (18GB)
├── loras/
│   ├── WanAnimate_relight_lora_fp16.safetensors (1.4GB)
│   └── lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors (704MB)
├── text_encoders/
│   └── umt5_xxl_fp8_e4m3fn_scaled.safetensors (6.3GB)
├── clip_vision/
│   └── clip_vision_h.safetensors (1.2GB)
└── vae/
    └── wan_2.1_vae.safetensors (243MB)
```

### Custom Nodes

- [comfyui_controlnet_aux](https://github.com/Fannovel16/comfyui_controlnet_aux) - DWPreprocessor
- [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes/) - PointsEditor, DrawMaskOnImage
- [ComfyUI-segment-anything-2](https://github.com/kijai/ComfyUI-segment-anything-2) - SAM2 segmentation

## 🚀 Deploy lên RunPod

### Bước 1: Push code lên GitHub

```bash
cd wan-animate-runpod
git init
git add .
git commit -m "Initial commit: Wan Animate 14B endpoint"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/wan-animate-runpod.git
git push -u origin main
```

### Bước 2: Tạo Serverless Endpoint

1. Vào [RunPod Serverless](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**
3. Chọn **"Deploy from GitHub"**
4. Nhập GitHub repository URL
5. **Attach Network Volume** (chứa models đã download)
6. Cấu hình:
   - **Container Disk**: 20GB
   - **GPU**: RTX 4090 hoặc A100
   - **Max Workers**: 1-3 (tùy budget)
   - **Idle Timeout**: 60s
   - **Execution Timeout**: 600s (10 phút)

### Bước 3: Environment Variables

Không cần environment variables đặc biệt.

## 📡 API Usage

### Request Format

```json
{
  "input": {
    "video_url": "https://example.com/video.mp4",
    "reference_image_url": "https://example.com/character.png",
    "positive_prompt": "The character is dancing in the room",
    "negative_prompt": "色调艳丽，过曝，静态，细节模糊不清",
    "width": 640,
    "height": 640,
    "seed": -1,
    "steps": 6,
    "cfg": 1.0,
    "sampler_name": "euler",
    "scheduler": "simple",
    "fps": 16
  }
}
```

### Response Format

```json
{
  "status": "success",
  "prompt_id": "abc123",
  "output": {
    "videos": [
      {
        "filename": "output_video.mp4",
        "subfolder": "video/ComfyUI",
        "type": "output"
      }
    ]
  }
}
```

### Example với RunPod SDK

```python
import runpod

runpod.api_key = "YOUR_RUNPOD_API_KEY"

endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

request = endpoint.run({
    "video_url": "https://example.com/dance.mp4",
    "reference_image_url": "https://example.com/character.png",
    "positive_prompt": "A beautiful girl dancing gracefully",
    "width": 640,
    "height": 640,
    "steps": 6
})

# Wait for completion
result = request.output()
print(result)
```

## 🎨 Workflow Details

Workflow sử dụng:
- **DWPreprocessor**: Trích xuất pose và face từ video gốc
- **SAM2**: Tạo character mask tự động
- **Wan2.2 Animate 14B**: Generate video với character mới
- **LoRAs**: Tăng chất lượng lighting và details

## 💰 Chi phí ước tính

- **Network Volume**: $15/tháng (150GB)
- **Serverless Execution**: 
  - RTX 4090: ~$0.50/phút
  - A100: ~$1.00/phút
- **Video 16 frames (~1s)**: ~$0.50-1.00 per video

## 🔧 Troubleshooting

### Models không load được
- Kiểm tra Network Volume đã được attach đúng
- Verify symlinks trong Dockerfile

### Out of Memory
- Giảm `width` và `height` xuống 512x512
- Sử dụng GPU có VRAM lớn hơn (A100 40GB)

### Timeout
- Tăng `Execution Timeout` trong endpoint settings
- Giảm số `steps` xuống 4-6

## 📚 Resources

- [ComfyUI Documentation](https://docs.comfy.org/)
- [Wan Video Models](https://huggingface.co/Kijai/WanVideo_comfy)
- [RunPod Serverless Docs](https://docs.runpod.io/serverless/overview)

## 📄 License

MIT License - Free to use for commercial and personal projects.
