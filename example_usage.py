"""
Example script to test Wan Animate RunPod endpoint
"""

import runpod
import time

# Configuration
RUNPOD_API_KEY = "YOUR_API_KEY_HERE"
ENDPOINT_ID = "YOUR_ENDPOINT_ID_HERE"

# Initialize
runpod.api_key = RUNPOD_API_KEY
endpoint = runpod.Endpoint(ENDPOINT_ID)

# Example request
request_data = {
    "video_url": "https://example.com/dance_video.mp4",
    "reference_image_url": "https://example.com/character.png",
    "positive_prompt": "A beautiful anime girl dancing gracefully in a modern room",
    "negative_prompt": "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止",
    "width": 640,
    "height": 640,
    "seed": -1,  # Random seed
    "steps": 6,
    "cfg": 1.0,
    "sampler_name": "euler",
    "scheduler": "simple",
    "fps": 16
}

print("Sending request to endpoint...")
print(f"Video URL: {request_data['video_url']}")
print(f"Reference Image: {request_data['reference_image_url']}")
print(f"Prompt: {request_data['positive_prompt']}")

# Run async request
request = endpoint.run(request_data)

print(f"\nRequest ID: {request.request_id}")
print("Status: Processing...")

# Poll for status
while True:
    status = request.status()
    print(f"Status: {status}")
    
    if status in ["COMPLETED", "FAILED"]:
        break
    
    time.sleep(5)

# Get result
if status == "COMPLETED":
    result = request.output()
    print("\n✅ Success!")
    print(f"Result: {result}")
    
    # Extract video URL if available
    if "output" in result and "videos" in result["output"]:
        videos = result["output"]["videos"]
        print(f"\nGenerated {len(videos)} video(s):")
        for video in videos:
            print(f"  - {video['filename']}")
else:
    error = request.output()
    print(f"\n❌ Failed: {error}")
