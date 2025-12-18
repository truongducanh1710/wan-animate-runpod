import runpod
import json
import os
import time
import requests
import subprocess
import base64
from io import BytesIO

COMFYUI_URL = "http://127.0.0.1:8188"

def start_comfyui():
    """Start ComfyUI server in background"""
    print("Starting ComfyUI server...")
    
    process = subprocess.Popen(
        ["python", "/comfyui/main.py", "--listen", "0.0.0.0", "--port", "8188"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    max_retries = 60
    for i in range(max_retries):
        try:
            response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
            if response.status_code == 200:
                print("✅ ComfyUI server started successfully")
                return process
        except Exception as e:
            if i % 10 == 0:
                print(f"Waiting for ComfyUI to start... ({i}/{max_retries})")
            time.sleep(2)
    
    raise Exception("Failed to start ComfyUI server")

def upload_file_to_comfyui(file_url, filename, subfolder="input"):
    """Download file from URL and upload to ComfyUI"""
    print(f"Downloading {filename} from {file_url}")
    
    # Download file
    response = requests.get(file_url, timeout=300)
    response.raise_for_status()
    
    # Upload to ComfyUI
    url = f"{COMFYUI_URL}/upload/image"
    files = {'image': (filename, BytesIO(response.content))}
    data = {'subfolder': subfolder, 'overwrite': 'true'}
    
    upload_response = requests.post(url, files=files, data=data, timeout=60)
    upload_response.raise_for_status()
    
    print(f"✅ Uploaded {filename} to ComfyUI")
    return upload_response.json()

def queue_prompt(workflow):
    """Queue workflow to ComfyUI"""
    url = f"{COMFYUI_URL}/prompt"
    response = requests.post(url, json={"prompt": workflow}, timeout=30)
    response.raise_for_status()
    return response.json()

def get_history(prompt_id):
    """Get execution history"""
    url = f"{COMFYUI_URL}/history/{prompt_id}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def wait_for_completion(prompt_id, timeout=3600):
    """Wait for workflow completion"""
    start_time = time.time()
    
    while True:
        if time.time() - start_time > timeout:
            raise Exception(f"Workflow execution timeout after {timeout}s")
        
        try:
            history = get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id]
        except Exception as e:
            print(f"Error checking history: {e}")
        
        time.sleep(5)

def handler(job):
    """
    RunPod handler function for Wan Animate 14B
    
    Input format:
    {
        "video_url": "https://...",
        "reference_image_url": "https://...",
        "positive_prompt": "The character is dancing",
        "negative_prompt": "...",
        "width": 640,
        "height": 640,
        "seed": -1,
        "steps": 6,
        "cfg": 1.0,
        "sampler_name": "euler",
        "scheduler": "simple",
        "fps": 16
    }
    """
    try:
        job_input = job['input']
        
        # Load workflow template
        with open('/workflows/wan_animate_workflow.json', 'r') as f:
            workflow = json.load(f)
        
        # Extract inputs with defaults
        video_url = job_input.get('video_url')
        reference_image_url = job_input.get('reference_image_url')
        positive_prompt = job_input.get('positive_prompt', 'The character is dancing in the room')
        negative_prompt = job_input.get('negative_prompt', '色调艳丽，过曝，静态，细节模糊不清')
        width = job_input.get('width', 640)
        height = job_input.get('height', 640)
        seed = job_input.get('seed', -1)
        steps = job_input.get('steps', 6)
        cfg = job_input.get('cfg', 1.0)
        sampler_name = job_input.get('sampler_name', 'euler')
        scheduler = job_input.get('scheduler', 'simple')
        fps = job_input.get('fps', 16)
        
        # Validate required inputs
        if not video_url:
            return {"error": "video_url is required"}
        if not reference_image_url:
            return {"error": "reference_image_url is required"}
        
        # Upload video
        print("Uploading video...")
        video_filename = "input_video.mp4"
        upload_file_to_comfyui(video_url, video_filename)
        
        # Upload reference image
        print("Uploading reference image...")
        img_filename = "reference_image.png"
        upload_file_to_comfyui(reference_image_url, img_filename)
        
        # Update workflow with inputs
        nodes = {node['id']: node for node in workflow['nodes']}
        
        # Update video loader (node 145)
        if 145 in nodes:
            nodes[145]['widgets_values'][0] = video_filename
        
        # Update reference image (node 10)
        if 10 in nodes:
            nodes[10]['widgets_values'][0] = img_filename
        
        # Update prompts
        if 21 in nodes:  # Positive prompt
            nodes[21]['widgets_values'][0] = positive_prompt
        if 1 in nodes:  # Negative prompt
            nodes[1]['widgets_values'][0] = negative_prompt
        
        # Update dimensions
        if 159 in nodes:  # Width
            nodes[159]['widgets_values'][0] = width
        if 160 in nodes:  # Height
            nodes[160]['widgets_values'][0] = height
        
        # Update sampling parameters (node 232 - first sampling group)
        if 232 in nodes:
            # Find seed widget index and update
            nodes[232]['widgets_values'][3] = seed  # seed
            nodes[232]['widgets_values'][4] = steps  # steps
            nodes[232]['widgets_values'][5] = cfg  # cfg
            nodes[232]['widgets_values'][6] = sampler_name
            nodes[232]['widgets_values'][7] = scheduler
            nodes[232]['widgets_values'][2] = fps
        
        print("Queueing workflow...")
        result = queue_prompt(workflow)
        prompt_id = result['prompt_id']
        
        print(f"Workflow queued with ID: {prompt_id}")
        print("Waiting for completion...")
        
        # Wait for completion
        history = wait_for_completion(prompt_id)
        
        # Extract output video URL
        outputs = history.get('outputs', {})
        
        # Find SaveVideo node output (node 19)
        video_output = None
        for node_id, node_output in outputs.items():
            if 'gifs' in node_output or 'videos' in node_output:
                video_output = node_output
                break
        
        if not video_output:
            return {
                "status": "completed",
                "prompt_id": prompt_id,
                "message": "Workflow completed but no video output found",
                "outputs": outputs
            }
        
        return {
            "status": "success",
            "prompt_id": prompt_id,
            "output": video_output
        }
        
    except Exception as e:
        print(f"Error in handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Start ComfyUI server on container startup
print("Initializing ComfyUI...")
comfyui_process = start_comfyui()

# Start RunPod handler
print("Starting RunPod serverless handler...")
runpod.serverless.start({"handler": handler})
