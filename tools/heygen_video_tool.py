"""
HeyGen Video Tool - Create professional videos using HeyGen API
"""

import os
import requests
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any


def create_heygen_video(
    script: str,
    title: str = "Viral Moment",
    voice_id: str = "1bd001e7-c4d1-4d0a-9c7e-2c4c5c5c5c5c"  # Default HeyGen voice
) -> str:
    """
    Create a professional video using HeyGen API with high-quality audio
    
    Args:
        script (str): The script text to convert to video
        title (str): Video title
        voice_id (str): HeyGen voice ID
        
    Returns:
        str: Path to the generated video file
    """
    try:
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Get API key from environment
        api_key = os.getenv('HEYGEN_API_KEY')
        if not api_key:
            raise Exception("HEYGEN_API_KEY not found in environment variables")
        
        # Step 1: Create video task
        print("🎬 Creating HeyGen video task...")
        task_id = create_heygen_task(script, voice_id, title)
        
        # Step 2: Wait for video generation
        print("⏳ Waiting for video generation...")
        video_url = wait_for_video_completion(task_id, api_key)
        
        # Step 3: Download video
        print("📥 Downloading generated video...")
        video_path = download_heygen_video(video_url, output_dir, title)
        
        print(f"✅ HeyGen video created successfully: {video_path}")
        return video_path
        
    except Exception as e:
        raise Exception(f"Failed to create HeyGen video: {str(e)}")


def create_heygen_task(script: str, voice_id: str, title: str) -> str:
    """
    Create a video generation task in HeyGen
    
    Args:
        script (str): Script text
        voice_id (str): HeyGen voice ID
        title (str): Video title
        
    Returns:
        str: Task ID
    """
    try:
        api_key = os.getenv('HEYGEN_API_KEY')
        
        # HeyGen API endpoint for creating video
        url = "https://api.heygen.com/v1/video/generate"
        
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        # Prepare the video generation request
        data = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": "1bd001e7-c4d1-4d0a-9c7e-2c4c5c5c5c5c",  # Professional avatar
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script,
                        "voice_id": voice_id,
                        "speed": 1.0,
                        "emotion": "friendly"
                    },
                    "background": {
                        "type": "color",
                        "value": "#1a1a2e"
                    }
                }
            ],
            "dimension": {
                "width": 720,
                "height": 1280
            },
            "aspect_ratio": "9:16"
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code} - {response.text}")
        
        result = response.json()
        task_id = result.get("data", {}).get("video_id")
        
        if not task_id:
            raise Exception("Failed to get task ID from HeyGen response")
        
        print(f"✅ HeyGen task created: {task_id}")
        return task_id
        
    except Exception as e:
        raise Exception(f"Failed to create HeyGen task: {str(e)}")


def wait_for_video_completion(task_id: str, api_key: str, max_wait_time: int = 300) -> str:
    """
    Wait for video generation to complete
    
    Args:
        task_id (str): HeyGen task ID
        api_key (str): HeyGen API key
        max_wait_time (int): Maximum wait time in seconds
        
    Returns:
        str: Video URL
    """
    try:
        url = f"https://api.heygen.com/v1/video/{task_id}"
        headers = {"X-API-KEY": api_key}
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"HeyGen status check error: {response.status_code} - {response.text}")
            
            result = response.json()
            status = result.get("data", {}).get("status")
            
            if status == "completed":
                video_url = result.get("data", {}).get("video_url")
                if video_url:
                    print("✅ Video generation completed!")
                    return video_url
                else:
                    raise Exception("Video completed but no URL found")
            elif status == "failed":
                error_msg = result.get("data", {}).get("error_message", "Unknown error")
                raise Exception(f"Video generation failed: {error_msg}")
            elif status in ["pending", "processing"]:
                print(f"⏳ Video status: {status}, waiting...")
                time.sleep(10)  # Wait 10 seconds before checking again
            else:
                print(f"⚠️ Unknown status: {status}")
                time.sleep(10)
        
        raise Exception(f"Video generation timed out after {max_wait_time} seconds")
        
    except Exception as e:
        raise Exception(f"Failed to wait for video completion: {str(e)}")


def download_heygen_video(video_url: str, output_dir: Path, title: str) -> str:
    """
    Download the generated video from HeyGen
    
    Args:
        video_url (str): URL of the generated video
        output_dir (Path): Output directory
        title (str): Video title
        
    Returns:
        str: Path to downloaded video
    """
    try:
        # Generate filename
        timestamp = int(time.time())
        filename = f"heygen_{title.replace(' ', '_')}_{timestamp}.mp4"
        video_path = output_dir / filename
        
        # Download video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Video downloaded: {video_path}")
        return str(video_path)
        
    except Exception as e:
        raise Exception(f"Failed to download HeyGen video: {str(e)}")


def get_heygen_voices() -> list[Dict[str, Any]]:
    """
    Get list of available HeyGen voices
    
    Returns:
        list: List of available voices
    """
    try:
        api_key = os.getenv('HEYGEN_API_KEY')
        if not api_key:
            raise Exception("HEYGEN_API_KEY not found in environment variables")
        
        url = "https://api.heygen.com/v1/voice.list"
        headers = {"X-API-KEY": api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code} - {response.text}")
        
        result = response.json()
        voices = result.get("data", {}).get("voices", [])
        
        return voices
        
    except Exception as e:
        raise Exception(f"Failed to get HeyGen voices: {str(e)}")


def get_heygen_avatars() -> list[Dict[str, Any]]:
    """
    Get list of available HeyGen avatars
    
    Returns:
        list: List of available avatars
    """
    try:
        api_key = os.getenv('HEYGEN_API_KEY')
        if not api_key:
            raise Exception("HEYGEN_API_KEY not found in environment variables")
        
        url = "https://api.heygen.com/v1/avatar.list"
        headers = {"X-API-KEY": api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"HeyGen API error: {response.status_code} - {response.text}")
        
        result = response.json()
        avatars = result.get("data", {}).get("avatars", [])
        
        return avatars
        
    except Exception as e:
        raise Exception(f"Failed to get HeyGen avatars: {str(e)}")


if __name__ == "__main__":
    print("HeyGen Video Tool created successfully!")
    print("Available functions:")
    print("- create_heygen_video()")
    print("- get_heygen_voices()")
    print("- get_heygen_avatars()")
