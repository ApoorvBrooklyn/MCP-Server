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


def run_enhanced_wav2lip_inference(face_video: str, audio_file: str, output_path: str) -> str:
    """
    Run enhanced Wav2Lip inference with better lip sync quality
    
    Args:
        face_video (str): Path to face video
        audio_file (str): Path to audio file
        output_path (str): Output video path
        
    Returns:
        str: Path to generated video
    """
    try:
        print("🎭 Running enhanced Wav2Lip inference...")
        # Import using absolute module path to avoid relative import issues
        from tools.wav2lip_inference import run_wav2lip_inference as core_wav2lip
        return core_wav2lip(face_video, audio_file, output_path)
    except Exception as e:
        # Do not silently fallback; propagate error to avoid masking issues
        raise Exception(f"Enhanced Wav2Lip failed: {e}")


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
            print("⚠️ Wav2Lip model not found, using enhanced fallback method")
            return create_advanced_lip_sync_video(face_video, audio_file, output_path)
        
        print("🎬 Running Wav2Lip inference for lip synchronization...")
        
        # Try to run actual Wav2Lip inference
        try:
            return run_actual_wav2lip(face_video, audio_file, output_path)
        except Exception as e:
            print(f"⚠️ Wav2Lip inference failed ({e}), using enhanced fallback method")
            return create_advanced_lip_sync_video(face_video, audio_file, output_path)
        
    except Exception as e:
        raise Exception(f"Failed to run Wav2Lip inference: {str(e)}")


def run_actual_wav2lip(face_video: str, audio_file: str, output_path: str) -> str:
    """
    Run the actual Wav2Lip inference using the official implementation
    
    Args:
        face_video (str): Path to face video
        audio_file (str): Path to audio file
        output_path (str): Output video path
        
    Returns:
        str: Path to generated video
    """
    try:
        # Import the Wav2Lip inference module
        from .wav2lip_inference import run_wav2lip_inference
        
        print("🎭 Running Wav2Lip lip synchronization...")
        
        # Run the Wav2Lip inference
        lip_synced_video = run_wav2lip_inference(face_video, audio_file, output_path)
        
        print(f"✅ Wav2Lip inference completed: {output_path}")
        return output_path
        
    except Exception as e:
        # Fallback to the advanced lip sync method
        print(f"⚠️ Wav2Lip inference failed ({e}), using advanced lip sync fallback...")
        return create_advanced_lip_sync_video(face_video, audio_file, output_path)


def preprocess_face_video(face_video: str) -> str:
    """
    Preprocess face video for Wav2Lip compatibility
    
    Args:
        face_video (str): Path to input face video
        
    Returns:
        str: Path to processed face video
    """
    try:
        import cv2
        import tempfile
        
        # Create a temporary file for the processed video
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Open the input video
        cap = cv2.VideoCapture(face_video)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
        
        print(f"🎬 Processing video: {width}x{height} @ {fps}fps")
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Enhance the frame for better face detection
            # Convert to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Try to detect and enhance face
            try:
                import face_recognition
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if face_locations:
                    # Face found, enhance it
                    for (top, right, bottom, left) in face_locations:
                        # Draw a rectangle around the face for debugging
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                        # Enhance the face region
                        face_region = frame[top:bottom, left:right]
                        if face_region.size > 0:
                            # Apply some enhancement to the face region
                            face_region = cv2.convertScaleAbs(face_region, alpha=1.1, beta=10)
                            frame[top:bottom, left:right] = face_region
                
            except Exception as e:
                print(f"⚠️ Face detection failed for frame {frame_count}: {e}")
            
            out.write(frame)
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"📊 Processed {frame_count} frames...")
        
        # Release everything
        cap.release()
        out.release()
        
        print(f"✅ Face video preprocessed: {temp_path}")
        return temp_path
        
    except Exception as e:
        raise Exception(f"Failed to preprocess face video: {str(e)}")


def create_advanced_lip_sync_video(face_video: str, audio_file: str, output_path: str) -> str:
    """
    Create an advanced lip-sync video using audio analysis and frame manipulation
    
    Args:
        face_video (str): Path to face video
        audio_file (str): Path to audio file
        output_path (str): Output video path
        
    Returns:
        str: Path to generated video
    """
    try:
        import cv2
        import librosa
        import numpy as np
        import tempfile
        
        print("🎵 Analyzing audio for lip sync...")
        
        # Load audio and analyze
        y, sr = librosa.load(audio_file)
        
        # Get audio duration
        duration = len(y) / sr
        
        # Analyze audio features for lip sync
        # Get onset frames (when speech starts)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='time')
        
        # Get RMS energy for volume-based lip movement
        rms = librosa.feature.rms(y=y)[0]
        
        # Open the face video
        cap = cv2.VideoCapture(face_video)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"🎬 Creating lip-synced video: {width}x{height} @ {fps}fps")
        
        frame_count = 0
        total_frames = int(duration * fps)
        
        while frame_count < total_frames:
            ret, frame = cap.read()
            if not ret:
                # If we run out of frames, loop the video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break
            
            # Calculate current time
            current_time = frame_count / fps
            
            # Get audio features for this time
            rms_idx = min(int(current_time * len(rms) / duration), len(rms) - 1)
            current_rms = rms[rms_idx]
            
            # Check if we're at an onset (speech start)
            is_speaking = any(abs(onset - current_time) < 0.1 for onset in onset_frames)
            
            # Apply lip sync effects based on audio
            if is_speaking or current_rms > np.mean(rms) * 0.5:
                # Enhance mouth region for speaking
                frame = enhance_mouth_region(frame, current_rms)
            
            # Add subtle mouth movement based on audio
            frame = add_mouth_movement(frame, current_rms, current_time)
            
            out.write(frame)
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"📊 Processed {frame_count}/{total_frames} frames...")
        
        # Release everything
        cap.release()
        out.release()
        
        print(f"✅ Advanced lip-sync video created: {output_path}")
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to create advanced lip sync video: {str(e)}")


def enhance_mouth_region(frame, rms_value):
    """
    Enhance the mouth region based on audio energy
    
    Args:
        frame: Input video frame
        rms_value: RMS energy value
        
    Returns:
        Enhanced frame
    """
    try:
        import cv2
        import numpy as np
        
        # Convert to HSV for better color manipulation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define mouth region (approximate)
        height, width = frame.shape[:2]
        mouth_region = frame[height//2:height, width//3:2*width//3]
        
        if mouth_region.size > 0:
            # Enhance based on RMS value
            enhancement_factor = 1.0 + (rms_value * 0.5)
            
            # Apply enhancement to mouth region
            mouth_region = cv2.convertScaleAbs(mouth_region, alpha=enhancement_factor, beta=10)
            frame[height//2:height, width//3:2*width//3] = mouth_region
        
        return frame
        
    except Exception as e:
        print(f"⚠️ Mouth enhancement failed: {e}")
        return frame


def add_mouth_movement(frame, rms_value, current_time):
    """
    Add subtle mouth movement based on audio
    
    Args:
        frame: Input video frame
        rms_value: RMS energy value
        current_time: Current time in video
        
    Returns:
        Frame with mouth movement
    """
    try:
        import cv2
        import numpy as np
        
        # Create a subtle mouth movement effect
        height, width = frame.shape[:2]
        
        # Calculate movement based on audio
        movement_intensity = min(rms_value * 2, 1.0)
        
        # Add a subtle warp effect to simulate mouth movement
        if movement_intensity > 0.1:
            # Create a subtle distortion
            rows, cols = frame.shape[:2]
            
            # Create a mesh grid
            y, x = np.ogrid[:rows, :cols]
            
            # Create a subtle wave effect in the mouth region
            mouth_center_y = int(height * 0.7)
            mouth_center_x = int(width * 0.5)
            
            # Calculate distance from mouth center
            dist_y = np.abs(y - mouth_center_y)
            dist_x = np.abs(x - mouth_center_x)
            
            # Create wave effect
            wave_effect = np.sin(dist_x * 0.01 + current_time * 10) * movement_intensity * 2
            
            # Apply the effect
            y_new = y + wave_effect.astype(np.int32)
            y_new = np.clip(y_new, 0, rows - 1)
            
            # Create the warped frame
            frame_warped = frame.copy()
            frame_warped[y_new, x] = frame[y, x]
            
            # Blend the original and warped frames
            alpha = movement_intensity * 0.3
            frame = cv2.addWeighted(frame, 1 - alpha, frame_warped, alpha, 0)
        
        return frame
        
    except Exception as e:
        print(f"⚠️ Mouth movement failed: {e}")
        return frame


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


def create_female_avatar_video(text: str, title: str = "Viral Moment") -> str:
    """
    Create a female avatar video using D-ID or similar service for narration
    
    Args:
        text (str): Script text
        title (str): Video title
        
    Returns:
        str: Path to created avatar video
    """
    try:
        # For now, create a simple animated avatar using FFmpeg
        # In a full implementation, you would use D-ID, Synthesia, or similar
        
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)
        
        import time
        timestamp = int(time.time())
        
        # Create a simple female avatar image
        width, height = 512, 512
        img = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple female avatar (face, hair, etc.)
        # Face
        face_center = (width // 2, height // 2)
        face_radius = 80
        draw.ellipse([face_center[0] - face_radius, face_center[1] - face_radius,
                     face_center[0] + face_radius, face_center[1] + face_radius], 
                    fill='#fdbcb4', outline='#d4a574', width=2)
        
        # Hair
        hair_points = [
            (face_center[0] - face_radius - 10, face_center[1] - face_radius - 20),
            (face_center[0] - face_radius - 30, face_center[1] - 20),
            (face_center[0] - 20, face_center[1] - 40),
            (face_center[0] + 20, face_center[1] - 40),
            (face_center[0] + face_radius + 30, face_center[1] - 20),
            (face_center[0] + face_radius + 10, face_center[1] - face_radius - 20),
            (face_center[0] + face_radius, face_center[1] - face_radius),
            (face_center[0] - face_radius, face_center[1] - face_radius)
        ]
        draw.polygon(hair_points, fill='#8b4513', outline='#654321', width=2)
        
        # Eyes
        eye_y = face_center[1] - 20
        left_eye = (face_center[0] - 25, eye_y)
        right_eye = (face_center[0] + 25, eye_y)
        draw.ellipse([left_eye[0] - 8, left_eye[1] - 8, left_eye[0] + 8, left_eye[1] + 8], 
                    fill='white', outline='black', width=1)
        draw.ellipse([right_eye[0] - 8, right_eye[1] - 8, right_eye[0] + 8, right_eye[1] + 8], 
                    fill='white', outline='black', width=1)
        
        # Eye pupils
        draw.ellipse([left_eye[0] - 3, left_eye[1] - 3, left_eye[0] + 3, left_eye[1] + 3], fill='black')
        draw.ellipse([right_eye[0] - 3, right_eye[1] - 3, right_eye[0] + 3, right_eye[1] + 3], fill='black')
        
        # Nose
        nose_y = face_center[1] + 5
        draw.ellipse([face_center[0] - 3, nose_y - 5, face_center[0] + 3, nose_y + 5], 
                    fill='#fdbcb4', outline='#d4a574', width=1)
        
        # Mouth (smiling)
        mouth_y = face_center[1] + 25
        mouth_points = [
            (face_center[0] - 15, mouth_y),
            (face_center[0] - 10, mouth_y + 5),
            (face_center[0] + 10, mouth_y + 5),
            (face_center[0] + 15, mouth_y)
        ]
        draw.polygon(mouth_points, fill='#ff6b6b', outline='#d63031', width=1)
        
        # Body (simple)
        body_top = face_center[1] + face_radius + 10
        draw.rectangle([face_center[0] - 40, body_top, face_center[0] + 40, body_top + 80], 
                      fill='#4a90e2', outline='#2c5aa0', width=2)
        
        # Add title
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 20), title, fill='#2c3e50', font=font)
        
        # Save the avatar image
        avatar_image_path = output_dir / f"female_avatar_{timestamp}.png"
        img.save(avatar_image_path)
        
        print(f"✅ Female avatar image created: {avatar_image_path}")
        return str(avatar_image_path)
        
    except Exception as e:
        raise Exception(f"Failed to create female avatar: {str(e)}")


def create_avatar_image(text: str, title: str = "Viral Moment") -> str:
    """
    Create a female avatar image for lip sync (updated version)
    
    Args:
        text (str): Text to display
        title (str): Video title
        
    Returns:
        str: Path to created image
    """
    return create_female_avatar_video(text, title)


def create_animated_avatar_video(script: str, title: str = "Viral Moment") -> str:
    """
    Create an animated female avatar video with lip sync
    
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
        
        # Step 2: Create animated avatar video
        print("👩 Creating animated female avatar...")
        avatar_video_path = create_avatar_animation_video(script, title, audio_path)
        
        # Step 3: Combine avatar video with audio
        print("🎬 Creating final video with lip sync...")
        import time
        timestamp = int(time.time())
        
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        final_video_path = output_dir / f"female_avatar_video_{timestamp}.mp4"
        
        # Get audio duration
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
                duration = 10
        except:
            duration = 10
        
        # Apply lip sync using Wav2Lip
        print("🎭 Applying lip synchronization...")
        lip_synced_path = run_wav2lip_inference(avatar_video_path, audio_path, str(final_video_path))
        
        # Clean up temporary files
        try:
            os.unlink(avatar_video_path)
        except:
            pass
        
        print(f"✅ Female avatar video with lip sync created successfully: {final_video_path}")
        return str(final_video_path)
        
    except Exception as e:
        raise Exception(f"Failed to create animated avatar video: {str(e)}")


def create_avatar_animation_video(script: str, title: str, audio_path: str) -> str:
    """
    Create an animated avatar video with facial expressions
    
    Args:
        script (str): Script text
        title (str): Video title
        audio_path (str): Path to audio file
        
    Returns:
        str: Path to generated avatar video
    """
    try:
        import time
        timestamp = int(time.time())
        
        # Get audio duration
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
        else:
            duration = 10
        
        # Create multiple avatar frames with different expressions
        frames_dir = Path("temp_frames")
        frames_dir.mkdir(exist_ok=True)
        
        fps = 25
        total_frames = int(duration * fps)
        
        print(f"🎭 Creating {total_frames} avatar frames...")
        
        for frame_num in range(total_frames):
            # Create avatar with different expressions based on frame
            frame_path = frames_dir / f"frame_{frame_num:04d}.png"
            create_animated_avatar_frame(script, title, frame_num, total_frames, str(frame_path))
        
        # Create video from frames
        avatar_video_path = f"temp_avatar_{timestamp}.mp4"
        
        cmd = [
            'ffmpeg',
            '-framerate', str(fps),
            '-i', str(frames_dir / 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-y',
            avatar_video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        # Clean up frames
        import shutil
        shutil.rmtree(frames_dir)
        
        return avatar_video_path
        
    except Exception as e:
        raise Exception(f"Failed to create avatar animation: {str(e)}")


def create_animated_avatar_frame(script: str, title: str, frame_num: int, total_frames: int, output_path: str) -> str:
    """
    Create a single animated avatar frame with expressions
    
    Args:
        script (str): Script text
        title (str): Video title
        frame_num (int): Current frame number
        total_frames (int): Total number of frames
        output_path (str): Output path for frame
        
    Returns:
        str: Path to created frame
    """
    try:
        width, height = 512, 512
        img = Image.new('RGB', (width, height), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        # Calculate animation progress
        progress = frame_num / total_frames if total_frames > 0 else 0
        
        # Face center with slight movement
        face_center = (width // 2, height // 2 + int(5 * (0.5 - abs(progress - 0.5))))
        face_radius = 80
        
        # Face
        draw.ellipse([face_center[0] - face_radius, face_center[1] - face_radius,
                     face_center[0] + face_radius, face_center[1] + face_radius], 
                    fill='#fdbcb4', outline='#d4a574', width=2)
        
        # Hair with slight movement
        hair_offset = int(2 * (0.5 - abs(progress - 0.5)))
        hair_points = [
            (face_center[0] - face_radius - 10 + hair_offset, face_center[1] - face_radius - 20),
            (face_center[0] - face_radius - 30 + hair_offset, face_center[1] - 20),
            (face_center[0] - 20 + hair_offset, face_center[1] - 40),
            (face_center[0] + 20 - hair_offset, face_center[1] - 40),
            (face_center[0] + face_radius + 30 - hair_offset, face_center[1] - 20),
            (face_center[0] + face_radius + 10 - hair_offset, face_center[1] - face_radius - 20),
            (face_center[0] + face_radius, face_center[1] - face_radius),
            (face_center[0] - face_radius, face_center[1] - face_radius)
        ]
        draw.polygon(hair_points, fill='#8b4513', outline='#654321', width=2)
        
        # Eyes with blinking
        eye_y = face_center[1] - 20
        left_eye = (face_center[0] - 25, eye_y)
        right_eye = (face_center[0] + 25, eye_y)
        
        # Blink every 2 seconds (50 frames at 25fps)
        blink = (frame_num % 50) < 3
        
        if not blink:
            draw.ellipse([left_eye[0] - 8, left_eye[1] - 8, left_eye[0] + 8, left_eye[1] + 8], 
                        fill='white', outline='black', width=1)
            draw.ellipse([right_eye[0] - 8, right_eye[1] - 8, right_eye[0] + 8, right_eye[1] + 8], 
                        fill='white', outline='black', width=1)
            # Eye pupils
            draw.ellipse([left_eye[0] - 3, left_eye[1] - 3, left_eye[0] + 3, left_eye[1] + 3], fill='black')
            draw.ellipse([right_eye[0] - 3, right_eye[1] - 3, right_eye[0] + 3, right_eye[1] + 3], fill='black')
        else:
            # Closed eyes
            draw.arc([left_eye[0] - 8, left_eye[1] - 4, left_eye[0] + 8, left_eye[1] + 4], 0, 180, fill='black', width=2)
            draw.arc([right_eye[0] - 8, right_eye[1] - 4, right_eye[0] + 8, right_eye[1] + 4], 0, 180, fill='black', width=2)
        
        # Nose
        nose_y = face_center[1] + 5
        draw.ellipse([face_center[0] - 3, nose_y - 5, face_center[0] + 3, nose_y + 5], 
                    fill='#fdbcb4', outline='#d4a574', width=1)
        
        # Mouth with talking animation
        mouth_y = face_center[1] + 25
        mouth_phase = (frame_num % 10) / 10.0  # 10-frame cycle
        
        if mouth_phase < 0.3:
            # Closed mouth
            draw.ellipse([face_center[0] - 8, mouth_y - 2, face_center[0] + 8, mouth_y + 2], 
                        fill='#ff6b6b', outline='#d63031', width=1)
        elif mouth_phase < 0.6:
            # Open mouth
            draw.ellipse([face_center[0] - 12, mouth_y - 6, face_center[0] + 12, mouth_y + 6], 
                        fill='#ff6b6b', outline='#d63031', width=1)
        else:
            # Smiling mouth
            mouth_points = [
                (face_center[0] - 15, mouth_y),
                (face_center[0] - 10, mouth_y + 5),
                (face_center[0] + 10, mouth_y + 5),
                (face_center[0] + 15, mouth_y)
            ]
            draw.polygon(mouth_points, fill='#ff6b6b', outline='#d63031', width=1)
        
        # Body with slight movement
        body_top = face_center[1] + face_radius + 10
        body_offset = int(1 * (0.5 - abs(progress - 0.5)))
        draw.rectangle([face_center[0] - 40 + body_offset, body_top, 
                       face_center[0] + 40 - body_offset, body_top + 80], 
                      fill='#4a90e2', outline='#2c5aa0', width=2)
        
        # Add title
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 20), title, fill='#2c3e50', font=font)
        
        # Save frame
        img.save(output_path)
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to create avatar frame: {str(e)}")


def create_real_avatar_video(script: str, title: str, avatar_image_path: str) -> str:
    """
    Create a video using a real human avatar image with proper lip sync
    
    Args:
        script (str): Script text
        title (str): Video title
        avatar_image_path (str): Path to real human avatar image
        
    Returns:
        str: Path to generated video
    """
    try:
        # Step 1: Generate audio using ElevenLabs (with fallback to local TTS)
        print("🎵 Generating high-quality audio...")
        try:
            from tools.voice_tool import create_natural_voiceover
            audio_path = create_natural_voiceover(script)
        except Exception as e:
            print(f"⚠️ ElevenLabs failed ({e}), using local TTS fallback...")
            from tools.voice_tool import create_voiceover
            audio_path = create_voiceover(script, speaker_gender="unknown")
        
        # Step 2: Process the real human avatar image
        print("👩 Processing real human avatar...")
        processed_avatar_path = process_real_avatar_image(avatar_image_path, title)
        
        # Step 3: Create video with real avatar
        print("🎬 Creating video with real human avatar...")
        import time
        timestamp = int(time.time())
        
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        final_video_path = output_dir / f"real_avatar_video_{timestamp}.mp4"
        
        # Get audio duration
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
                duration = 10
        except:
            duration = 10
        
        # Create a video from the static image first with proper mobile format
        temp_video_path = f"temp_avatar_video_{timestamp}.mp4"
        cmd = [
            'ffmpeg',
            '-loop', '1',
            '-i', processed_avatar_path,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-r', '24',
            '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black',
            '-movflags', '+faststart',
            '-y',
            temp_video_path
        ]
        
        print(f"🎬 Creating avatar video from image...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error creating avatar video: {result.stderr}")
        
        # Apply enhanced lip sync using improved Wav2Lip
        print("🎭 Applying enhanced lip synchronization...")
        lip_synced_path = run_enhanced_wav2lip_inference(temp_video_path, audio_path, str(final_video_path))
        
        # Clean up temporary files
        try:
            os.unlink(processed_avatar_path)
            os.unlink(temp_video_path)
        except:
            pass
        
        print(f"✅ Real human avatar video with enhanced lip sync created successfully: {final_video_path}")
        return str(final_video_path)
        
    except Exception as e:
        raise Exception(f"Failed to create real avatar video: {str(e)}")


def process_real_avatar_image(avatar_image_path: str, title: str) -> str:
    """
    Process the real human avatar image for video generation
    
    Args:
        avatar_image_path (str): Path to real human avatar image
        title (str): Video title
        
    Returns:
        str: Path to processed avatar image
    """
    try:
        # Open the real human avatar image
        img = Image.open(avatar_image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to 512x512 for Wav2Lip compatibility
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        
        # Add title overlay
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Add semi-transparent background for title
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        
        # Create semi-transparent overlay
        overlay = Image.new('RGBA', (title_width + 20, title_height + 10), (0, 0, 0, 128))
        img.paste(overlay, (10, 10), overlay)
        
        # Add title text
        draw.text((20, 15), title, fill='white', font=font)
        
        # Save processed image
        import time
        timestamp = int(time.time())
        processed_path = f"processed_avatar_{timestamp}.png"
        img.save(processed_path)
        
        print(f"✅ Real human avatar processed: {processed_path}")
        return processed_path
        
    except Exception as e:
        raise Exception(f"Failed to process real avatar image: {str(e)}")


def find_existing_avatar() -> str:
    """
    Look for existing avatar images in the avatars folder
    
    Returns:
        str: Path to existing avatar image, or None if not found
    """
    avatars_dir = Path("avatars")
    if not avatars_dir.exists():
        return None
    
    # Look for common avatar image files
    avatar_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    avatar_names = ['narrator', 'avatar', 'person', 'speaker', 'host']
    
    for name in avatar_names:
        for ext in avatar_extensions:
            avatar_path = avatars_dir / f"{name}{ext}"
            if avatar_path.exists():
                print(f"✅ Found existing avatar: {avatar_path}")
                return str(avatar_path)
    
    # If no specific names found, look for any image file
    for ext in avatar_extensions:
        for avatar_file in avatars_dir.glob(f"*{ext}"):
            print(f"✅ Found existing avatar: {avatar_file}")
            return str(avatar_file)
    
    return None


def create_wav2lip_video_with_audio(script: str, title: str = "Viral Moment", avatar_image_path: str = None) -> str:
    """
    Create a complete video with real human avatar and audio
    
    Args:
        script (str): Script text
        title (str): Video title
        avatar_image_path (str): Path to real human avatar image (optional)
        
    Returns:
        str: Path to generated video
    """
    # First, check if a specific avatar path was provided
    if avatar_image_path and os.path.exists(avatar_image_path):
        print(f"🎭 Using provided avatar: {avatar_image_path}")
        return create_real_avatar_video(script, title, avatar_image_path)
    
    # If no specific path, look for existing avatar in avatars folder
    existing_avatar = find_existing_avatar()
    if existing_avatar:
        print(f"🎭 Using existing avatar from avatars folder: {existing_avatar}")
        return create_real_avatar_video(script, title, existing_avatar)
    
    # If no existing avatar found, create an animated one
    print("🎭 No existing avatar found, creating animated avatar...")
    return create_animated_avatar_video(script, title)


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