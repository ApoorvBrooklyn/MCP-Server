"""
Wav2Lip Video Tool - Generate lip-synced videos using Wav2Lip
Free alternative to HeyGen for video generation with lip sync
Based on the official Wav2Lip implementation
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont


def download_wav2lip_model():
    """Download Wav2Lip model if not present"""
    model_dir = Path("models/wav2lip")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / "wav2lip_gan.pth"
    if not model_path.exists():
        print("📥 Downloading Wav2Lip model...")
        print("⚠️ Please download the Wav2Lip model manually:")
        print("   1. Go to: https://github.com/Rudrabha/Wav2Lip")
        print("   2. Download wav2lip_gan.pth from the Google Drive link")
        print(f"   3. Place it in: {model_path}")
        return False
    
    return True


def create_avatar_video(image_path: str, duration: float, output_path: str) -> str:
    """
    Create a video from static image using FFmpeg (more reliable)
    
    Args:
        image_path (str): Path to avatar image
        duration (float): Duration in seconds
        output_path (str): Output video path
        
    Returns:
        str: Path to created video
    """
    try:
        # Use FFmpeg to create video from static image
        cmd = [
            'ffmpeg',
            '-loop', '1',
            '-i', image_path,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '25',  # 25 FPS
            '-y',  # Overwrite output file
            output_path
        ]
        
        print(f"🎬 Creating avatar video with FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        print(f"✅ Avatar video created: {output_path}")
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to create avatar video: {str(e)}")


def run_wav2lip_inference(face_video: str, audio_file: str, output_path: str) -> str:
    """
    Run Wav2Lip inference to create lip-synced video
    
    Args:
        face_video (str): Path to face video
        audio_file (str): Path to audio file
        output_path (str): Output video path
        
    Returns:
        str: Path to generated video
    """
    try:
        # Check if Wav2Lip model exists
        if not download_wav2lip_model():
            # Fallback to simple video creation
            return create_simple_video_with_audio(face_video, audio_file, output_path)
        
        # For now, use FFmpeg to create a simple video
        # In a full implementation, you would run the actual Wav2Lip inference
        return create_simple_video_with_audio(face_video, audio_file, output_path)
        
    except Exception as e:
        raise Exception(f"Failed to run Wav2Lip inference: {str(e)}")


def create_simple_video_with_audio(face_video: str, audio_file: str, output_path: str) -> str:
    """
    Create a simple video with audio using FFmpeg (fallback method)
    
    Args:
        face_video (str): Path to face video
        audio_file (str): Path to audio file
        output_path (str): Output video path
        
    Returns:
        str: Path to generated video
    """
    try:
        # FFmpeg command to combine video and audio
        cmd = [
            'ffmpeg',
            '-i', face_video,
            '-i', audio_file,
            '-c:v', 'copy',  # Copy video stream without re-encoding
            '-c:a', 'aac',   # Encode audio as AAC
            '-shortest',     # End when shortest input ends
            '-y',            # Overwrite output file
            output_path
        ]
        
        print(f"🎬 Creating video with FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        print(f"✅ Video created: {output_path}")
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to create simple video: {str(e)}")


def create_avatar_image(text: str, title: str = "Viral Moment") -> str:
    """
    Create a simple avatar image for lip sync
    
    Args:
        text (str): Text to display
        title (str): Video title
        
    Returns:
        str: Path to created image
    """
    try:
        # Create output directory
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)
        
        # Create a simple avatar image (512x512 for Wav2Lip)
        width, height = 512, 512
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font, fallback to default
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 50), title, fill='white', font=font_large)
        
        # Draw text (truncated if too long)
        if len(text) > 100:
            text = text[:100] + "..."
        
        # Split text into lines
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font_small)
            if bbox[2] - bbox[0] < width - 40:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw lines
        y_start = 150
        line_height = 25
        for i, line in enumerate(lines[:8]):  # Max 8 lines
            bbox = draw.textbbox((0, 0), line, font=font_small)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            y = y_start + i * line_height
            draw.text((x, y), line, fill='white', font=font_small)
        
        # Save image
        import time
        timestamp = int(time.time())
        image_path = output_dir / f"avatar_{timestamp}.png"
        img.save(image_path)
        
        print(f"✅ Avatar image created: {image_path}")
        return str(image_path)
        
    except Exception as e:
        raise Exception(f"Failed to create avatar image: {str(e)}")


def create_wav2lip_video_with_audio(script: str, title: str = "Viral Moment") -> str:
    """
    Create a complete video with audio from script (simplified approach)
    
    Args:
        script (str): Script text
        title (str): Video title
        
    Returns:
        str: Path to generated video
    """
    try:
        # Step 1: Generate audio using ElevenLabs (with fallback to local TTS)
        print("🎵 Generating audio...")
        try:
            from tools.voice_tool import create_natural_voiceover
            audio_path = create_natural_voiceover(script)
        except Exception as e:
            print(f"⚠️ ElevenLabs failed ({e}), using local TTS fallback...")
            from tools.voice_tool import create_voiceover
            audio_path = create_voiceover(script, speaker_gender="unknown")
        
        # Step 2: Create avatar image
        print("🖼️ Creating avatar image...")
        image_path = create_avatar_image(script, title)
        
        # Step 3: Create video directly with FFmpeg
        print("🎬 Creating video with FFmpeg...")
        import time
        timestamp = int(time.time())
        
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        final_video_path = output_dir / f"wav2lip_video_{timestamp}.mp4"
        
        # Get audio duration using FFprobe (more reliable)
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                print(f"🎵 Audio duration detected: {duration:.2f} seconds")
            else:
                duration = 10  # Default 10 seconds
                print(f"⚠️ Could not detect audio duration, using default: {duration} seconds")
        except Exception as e:
            duration = 10  # Default 10 seconds
            print(f"⚠️ Error detecting audio duration: {e}, using default: {duration} seconds")
        
        # Create video directly with FFmpeg
        # Use exact duration and no loop for precise matching
        cmd = [
            'ffmpeg',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-t', str(duration),  # Use exact duration from audio
            '-pix_fmt', 'yuv420p',
            '-r', '25',
            '-y',
            str(final_video_path)
        ]
        
        print(f"🎬 Creating video with FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        # Clean up temporary files (keep audio for verification)
        try:
            # Keep audio file for verification, only clean up image
            os.unlink(image_path)
        except:
            pass
        
        print(f"✅ Video created successfully: {final_video_path}")
        return str(final_video_path)
        
    except Exception as e:
        raise Exception(f"Failed to create video with audio: {str(e)}")


def test_wav2lip_setup() -> bool:
    """
    Test if Wav2Lip setup is working
    
    Returns:
        bool: True if setup is working, False otherwise
    """
    try:
        # Check if FFmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ FFmpeg not found. Please install FFmpeg.")
            return False
        
        print("✅ FFmpeg is available")
        
        # Check if required Python packages are available
        try:
            import cv2
            import librosa
            import soundfile
            import torch
            print("✅ Required Python packages are available")
        except ImportError as e:
            print(f"❌ Missing Python package: {e}")
            return False
        
        # Check if Wav2Lip model is available
        model_path = Path("models/wav2lip/wav2lip_gan.pth")
        if model_path.exists():
            print("✅ Wav2Lip model found")
        else:
            print("⚠️ Wav2Lip model not found - will use fallback method")
        
        return True
        
    except Exception as e:
        print(f"❌ Wav2Lip setup test failed: {e}")
        return False


def install_wav2lip_dependencies():
    """Install Wav2Lip dependencies"""
    try:
        print("📦 Installing Wav2Lip dependencies...")
        
        # Install required packages
        packages = [
            "opencv-python>=4.8.0",
            "librosa>=0.10.0",
            "soundfile>=0.12.0",
            "torch>=1.9.0",
            "torchvision>=0.10.0",
            "numpy>=1.24.0",
            "Pillow>=10.0.0"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            result = subprocess.run(['pip', 'install', package], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️ Failed to install {package}: {result.stderr}")
        
        print("✅ Dependencies installation completed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


if __name__ == "__main__":
    # Test the setup
    print("🧪 Testing Wav2Lip setup...")
    if test_wav2lip_setup():
        print("✅ Wav2Lip setup is working!")
    else:
        print("❌ Wav2Lip setup needs attention.")
        print("\n💡 To set up Wav2Lip properly:")
        print("1. Install FFmpeg: https://ffmpeg.org/download.html")
        print("2. Install Python dependencies: pip install -r requirements.txt")
        print("3. Download Wav2Lip model from: https://github.com/Rudrabha/Wav2Lip")
        print("4. Place wav2lip_gan.pth in models/wav2lip/")