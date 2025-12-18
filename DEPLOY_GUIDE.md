# 🚀 Hướng dẫn Deploy Wan Animate 14B lên RunPod Serverless

## ✅ Checklist trước khi deploy

- [x] Network Volume đã tạo và có đầy đủ models (28GB)
- [ ] Workflow JSON đã paste vào `workflows/wan_animate_workflow.json`
- [ ] GitHub repository đã tạo
- [ ] Code đã push lên GitHub

---

## Bước 1: Chuẩn bị Workflow JSON

**Quan trọng**: Bạn cần copy workflow JSON vào file này:

```
wan-animate-runpod/workflows/wan_animate_workflow.json
```

Mở file đó và paste toàn bộ workflow JSON bạn đã cung cấp trước đó (bắt đầu từ `{"id": "ba1df054-50a8-4da2-b45a-25b4dde3cc2f"...}`).

---

## Bước 2: Tạo GitHub Repository

### 2.1. Tạo repo mới trên GitHub

1. Vào https://github.com/new
2. Repository name: `wan-animate-runpod`
3. Visibility: **Public** (để RunPod có thể truy cập)
4. **Không** tích "Initialize with README"
5. Click **Create repository**

### 2.2. Push code lên GitHub

Mở PowerShell trong thư mục `wan-animate-runpod`:

```powershell
cd "d:\APP\Affiliate workflow\wan-animate-runpod"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Wan Animate 14B serverless endpoint"

# Add remote (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/wan-animate-runpod.git

# Push
git branch -M main
git push -u origin main
```

---

## Bước 3: Deploy Serverless Endpoint trên RunPod

### 3.1. Tạo Endpoint mới

1. Vào https://www.runpod.io/console/serverless
2. Click **"+ New Endpoint"**

### 3.2. Cấu hình Endpoint

#### Tab "Select Template"
- Chọn **"Deploy from GitHub"**
- GitHub URL: `https://github.com/YOUR_USERNAME/wan-animate-runpod`
- Branch: `main`

#### Tab "Configure Endpoint"

**Basic Settings:**
- Endpoint Name: `wan-animate-14b`
- Container Disk: `20 GB`
- Container Registry Credentials: Để trống (public image)

**GPU Configuration:**
- GPU Types: Chọn **RTX 4090** hoặc **A100 40GB**
- Min Workers: `0` (auto-scale)
- Max Workers: `1-3` (tùy budget)

**Advanced Settings:**
- Idle Timeout: `60` seconds
- Execution Timeout: `600` seconds (10 phút)
- FlashBoot: Bật (nếu có)

#### Tab "Attach Network Volume"

**QUAN TRỌNG**: 
- Click **"Attach Network Volume"**
- Chọn Network Volume bạn đã tạo (chứa models)
- Mount Path: `/runpod-volume` (mặc định)

### 3.3. Deploy

Click **"Deploy"** và đợi:
- Build Docker image: ~10-15 phút
- Deploy endpoint: ~2-3 phút

---

## Bước 4: Test Endpoint

### 4.1. Lấy Endpoint ID và API Key

Sau khi deploy xong:
1. Copy **Endpoint ID** (dạng: `abc123def456`)
2. Vào **Settings** → **API Keys** → Copy API key

### 4.2. Test với RunPod SDK

```python
import runpod

runpod.api_key = "YOUR_API_KEY"

endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Test request
request = endpoint.run({
    "video_url": "https://example.com/test_video.mp4",
    "reference_image_url": "https://example.com/character.png",
    "positive_prompt": "A girl dancing in the room",
    "width": 640,
    "height": 640,
    "steps": 6
})

# Wait for result
result = request.output()
print(result)
```

### 4.3. Test với cURL

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "video_url": "https://example.com/video.mp4",
      "reference_image_url": "https://example.com/character.png",
      "positive_prompt": "Dancing character",
      "width": 640,
      "height": 640
    }
  }'
```

---

## Bước 5: Monitor và Debug

### 5.1. Xem Logs

1. Vào Endpoint → **Requests** tab
2. Click vào request để xem logs chi tiết

### 5.2. Common Issues

**Issue: "Models not found"**
- Kiểm tra Network Volume đã attach đúng
- Verify models trong `/runpod-volume/models/`

**Issue: "Out of memory"**
- Giảm `width` và `height` xuống 512
- Dùng GPU có VRAM lớn hơn

**Issue: "Timeout"**
- Tăng Execution Timeout lên 900s (15 phút)
- Giảm số `steps` xuống 4

---

## 🎉 Hoàn tất!

Endpoint của bạn đã sẵn sàng. Bây giờ bạn có thể:

1. **Tích hợp vào app**: Sử dụng endpoint này trong Affiliate workflow app
2. **Scale up**: Tăng Max Workers khi có nhiều traffic
3. **Monitor costs**: Theo dõi usage trong RunPod dashboard

---

## 💰 Chi phí dự kiến

- **Network Volume**: $15/tháng (150GB)
- **Serverless Execution**: 
  - Idle (0 workers): $0
  - Active (RTX 4090): ~$0.50/phút
  - Active (A100): ~$1.00/phút
- **Mỗi video (~16 frames)**: $0.50-1.00

**Lưu ý**: Chỉ tính phí khi có request, không tính khi idle!
