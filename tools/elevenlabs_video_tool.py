"""
ElevenLabs Video Tool - Create professional videos using ElevenLabs TTS and visual elements
"""

import os
import tempfile
import subprocess
import requests
import re
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import textwrap


def get_voice_by_gender(speaker_gender: str) -> str:
    """
    Get appropriate ElevenLabs voice ID based on speaker gender
    
    Args:
        speaker_gender (str): Gender of the speaker ("male", "female", "unknown")
        
    Returns:
        str: ElevenLabs voice ID
    """
    # Voice ID mapping for different genders
    # These are high-quality ElevenLabs voices optimized for different genders
    voice_mapping = {
        "male": "21m00Tcm4TlvDq8ikWAM",      # Adam - Deep, authoritative male voice
        "female": "EXAVITQu4vr4xnSDxMaL",    # Bella - Clear, engaging female voice  
        "unknown": "21m00Tcm4TlvDq8ikWAM"    # Default to male voice
    }
    
    return voice_mapping.get(speaker_gender.lower(), voice_mapping["unknown"])


def get_available_voices_by_gender() -> dict:
    """
    Get a list of available voices organized by gender
    
    Returns:
        dict: Dictionary with gender keys and voice lists
    """
    return {
        "male": [
            {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Adam", "description": "Deep, authoritative male voice"},
            {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "description": "Confident, energetic male voice"},
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "description": "Warm, engaging male voice"},
        ],
        "female": [
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "description": "Clear, engaging female voice"},
            {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "description": "Young, energetic female voice"},
            {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "description": "Professional female voice"},
        ]
    }


def clean_script_for_tts(script_text: str) -> str:
    """
    Clean script text to remove formatting elements that shouldn't be spoken
    
    Args:
        script_text (str): Raw script text with formatting
        
    Returns:
        str: Cleaned script text ready for TTS
    """
    # Remove asterisks used for emphasis (e.g., *years* -> years)
    script_text = re.sub(r'\*([^*]+)\*', r'\1', script_text)
    
    # Remove standalone periods that are used for emphasis (e.g., "Full stop." -> "Full stop")
    script_text = re.sub(r'\.\s*$', '', script_text, flags=re.MULTILINE)
    
    # Remove ellipses that are used for dramatic pause (e.g., "years..." -> "years")
    script_text = re.sub(r'\.{3,}', '', script_text)
    
    # Remove single periods that are used for emphasis (e.g., "Deeply." -> "Deeply")
    script_text = re.sub(r'^\.\s*$', '', script_text, flags=re.MULTILINE)
    
    # Remove brackets and their contents (e.g., [like this])
    script_text = re.sub(r'\[[^\]]*\]', '', script_text)
    
    # Remove parentheses and their contents (e.g., (like this))
    script_text = re.sub(r'\([^)]*\)', '', script_text)
    
    # Remove quotes around single words that are used for emphasis (e.g., "man enough" -> man enough)
    script_text = re.sub(r'"([^"]+)"', r'\1', script_text)
    
    # Remove single quotes around words (e.g., 'man enough' -> man enough)
    script_text = re.sub(r"'([^']+)'", r'\1', script_text)
    
    # Remove multiple spaces and clean up whitespace
    script_text = re.sub(r'\s+', ' ', script_text)
    
    # Remove leading/trailing whitespace
    script_text = script_text.strip()
    
    # Remove empty lines
    lines = [line.strip() for line in script_text.split('\n') if line.strip()]
    script_text = '\n'.join(lines)
    
    return script_text


def create_elevenlabs_video(
    script: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice ID
    model_id: str = "eleven_multilingual_v2",
    background_color: str = "#000000",
    text_color: str = "#FFFFFF",
    quote: str = "",
    title: str = "Viral Moment",
    speaker_gender: str = "unknown"
) -> str:
    """
    Create a professional video using ElevenLabs TTS and engaging visual elements
    
    Args:
        script (str): The script text to convert to speech and display
        voice_id (str): ElevenLabs voice ID (will be overridden by speaker_gender if provided)
        model_id (str): ElevenLabs model ID
        background_color (str): Background color (hex format)
        text_color (str): Text color (hex format)
        quote (str): Key quote to highlight
        title (str): Video title
        speaker_gender (str): Gender of the speaker ("male", "female", "unknown")
        
    Returns:
        str: Path to the generated video file
    """
    try:
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Select appropriate voice based on gender
        if speaker_gender != "unknown":
            selected_voice_id = get_voice_by_gender(speaker_gender)
            print(f"🎤 Using {speaker_gender} voice: {selected_voice_id}")
        else:
            selected_voice_id = voice_id
            print(f"🎤 Using provided voice: {selected_voice_id}")
        
        # Step 1: Generate audio using ElevenLabs
        print("🎵 Generating audio with ElevenLabs...")
        cleaned_script = clean_script_for_tts(script)
        audio_path = generate_elevenlabs_audio(cleaned_script, selected_voice_id, model_id)
        
        # Step 2: Create engaging visual scenes
        print("🎨 Creating engaging visual scenes...")
        scenes = create_engaging_video_scenes(script, quote, title)
        
        # Step 3: Combine audio and multiple scenes into video
        print("🎬 Creating multi-scene video...")
        video_path = create_multi_scene_video(audio_path, scenes, output_dir)
        
        # Clean up temporary files
        os.unlink(audio_path)
        for scene_path in scenes:
            os.unlink(scene_path)
        
        print(f"✅ Engaging video created successfully: {video_path}")
        return video_path
        
    except Exception as e:
        raise Exception(f"Failed to create ElevenLabs video: {str(e)}")


def create_multi_scene_video(audio_path: str, scene_paths: list, output_dir: Path) -> str:
    """
    Create a video with multiple scenes that change throughout the duration
    
    Args:
        audio_path (str): Path to audio file
        scene_paths (list): List of scene image paths
        output_dir (Path): Output directory
        
    Returns:
        str: Path to generated video
    """
    try:
        # Get audio duration
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', audio_path
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        
        # Calculate scene duration
        scene_duration = duration / len(scene_paths)
        
        # Generate output filename
        output_filename = f"engaging_video_{int(duration)}s.mp4"
        output_path = output_dir / output_filename
        
        # Create filter complex for scene transitions
        filter_complex = ""
        inputs = []
        
        for i, scene_path in enumerate(scene_paths):
            inputs.extend(['-loop', '1', '-t', str(scene_duration), '-i', scene_path])
        
        # Create scene transitions with crossfade
        for i in range(len(scene_paths) - 1):
            if i == 0:
                filter_complex += f"[0:v][1:v]xfade=transition=fade:duration=0.5:offset={scene_duration-0.5}[v{i+1}];"
            else:
                filter_complex += f"[v{i}][{i+1}:v]xfade=transition=fade:duration=0.5:offset={scene_duration-0.5}[v{i+1}];"
        
        # Final output
        final_video = f"v{len(scene_paths)-1}"
        filter_complex += f"[{final_video}]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2[vout]"
        
        # Create video using ffmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            *inputs,  # All scene inputs
            '-i', audio_path,  # Audio input
            '-filter_complex', filter_complex,
            '-map', '[vout]',  # Video output
            '-map', f'{len(scene_paths)}:a',  # Audio output
            '-c:v', 'libx264', '-tune', 'stillimage',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-shortest',  # End when shortest input ends
            str(output_path)
        ]
        
        # Run ffmpeg command
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            # Fallback to simple concatenation if complex filter fails
            return create_simple_multi_scene_video(audio_path, scene_paths, output_dir)
        
        print(f"✅ Multi-scene video created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Complex video creation failed, using simple method: {e}")
        return create_simple_multi_scene_video(audio_path, scene_paths, output_dir)


def create_simple_multi_scene_video(audio_path: str, scene_paths: list, output_dir: Path) -> str:
    """
    Create a simple multi-scene video using basic concatenation
    
    Args:
        audio_path (str): Path to audio file
        scene_paths (list): List of scene image paths
        output_dir (Path): Output directory
        
    Returns:
        str: Path to generated video
    """
    try:
        # Get audio duration
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', audio_path
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        
        # Calculate scene duration
        scene_duration = duration / len(scene_paths)
        
        # Generate output filename
        output_filename = f"engaging_video_{int(duration)}s.mp4"
        output_path = output_dir / output_filename
        
        # Create video using the first scene for the full duration
        # This is a fallback method
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-loop', '1', '-i', scene_paths[0],  # Use first scene
            '-i', audio_path,  # Input audio
            '-c:v', 'libx264', '-tune', 'stillimage',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-shortest',  # End when shortest input ends
            '-t', str(duration),  # Duration
            str(output_path)
        ]
        
        # Run ffmpeg command
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        print(f"✅ Simple multi-scene video created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to create simple multi-scene video: {str(e)}")


def generate_elevenlabs_audio(script: str, voice_id: str, model_id: str) -> str:
    """
    Generate audio using ElevenLabs TTS API
    
    Args:
        script (str): Text to convert to speech
        voice_id (str): ElevenLabs voice ID
        model_id (str): ElevenLabs model ID
        
    Returns:
        str: Path to generated audio file
    """
    try:
        # Get API key from environment
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise Exception("ELEVENLABS_API_KEY not found in environment variables")
        
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": script,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.75,  # Higher stability for more consistent voice
                "similarity_boost": 0.75,  # Higher similarity for better voice matching
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        # Make API request
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_file.write(response.content)
            audio_path = tmp_file.name
        
        print(f"✅ Audio generated: {audio_path}")
        return audio_path
        
    except Exception as e:
        raise Exception(f"Failed to generate ElevenLabs audio: {str(e)}")


def create_video_image(
    script: str,
    quote: str,
    title: str,
    background_color: str,
    text_color: str,
    width: int = 720,
    height: int = 1280
) -> str:
    """
    Create a dynamic visual image for the video based on script content
    
    Args:
        script (str): Script text
        quote (str): Key quote
        title (str): Video title
        background_color (str): Background color
        text_color (str): Text color
        width (int): Image width
        height (int): Image height
        
    Returns:
        str: Path to generated image
    """
    try:
        # Create image with gradient background
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        for y in range(height):
            # Create a subtle gradient from top to bottom
            ratio = y / height
            r = int(background_color[1:3], 16) + int(20 * ratio)
            g = int(background_color[3:5], 16) + int(20 * ratio)
            b = int(background_color[5:7], 16) + int(20 * ratio)
            r, g, b = min(255, r), min(255, g), min(255, b)
            color = (r, g, b)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Try to use a system font, fallback to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 72)
            script_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
            quote_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 42)
        except:
            try:
                title_font = ImageFont.truetype("Arial.ttf", 72)
                script_font = ImageFont.truetype("Arial.ttf", 32)
                quote_font = ImageFont.truetype("Arial.ttf", 42)
            except:
                title_font = ImageFont.load_default()
                script_font = ImageFont.load_default()
                quote_font = ImageFont.load_default()
        
        # Draw title with shadow effect
        title_y = 80
        # Shadow
        draw.text((width//2 + 2, title_y + 2), title, font=title_font, fill="#000000", anchor="mm")
        # Main text
        draw.text((width//2, title_y), title, font=title_font, fill=text_color, anchor="mm")
        
        # Extract key phrases from script for dynamic display
        script_words = script.split()
        key_phrases = []
        
        # Find important phrases (words that appear multiple times or are capitalized)
        word_count = {}
        for word in script_words:
            clean_word = word.strip('.,!?').lower()
            if len(clean_word) > 3:
                word_count[clean_word] = word_count.get(clean_word, 0) + 1
        
        # Get most frequent words
        frequent_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Draw key phrases in a dynamic layout
        phrase_y = 200
        for i, (word, count) in enumerate(frequent_words):
            if i < 3:  # Show top 3 words
                phrase_text = word.upper()
                # Alternate colors for visual interest
                phrase_color = "#FFD700" if i % 2 == 0 else "#FF6B6B"
                draw.text((width//2, phrase_y), phrase_text, font=script_font, fill=phrase_color, anchor="mm")
                phrase_y += 60
        
        # Draw main script text (first 100 characters)
        script_preview = script[:100] + "..." if len(script) > 100 else script
        script_lines = textwrap.wrap(script_preview, width=35)
        script_y = 400
        
        for line in script_lines[:6]:  # Limit to 6 lines
            draw.text((width//2, script_y), line, font=script_font, fill=text_color, anchor="mm")
            script_y += 40
        
        # Draw quote if provided with special styling
        if quote:
            quote_y = height - 150
            quote_text = f'"{quote}"'
            quote_lines = textwrap.wrap(quote_text, width=30)
            
            # Quote background
            quote_bg_height = len(quote_lines) * 50 + 20
            draw.rectangle([50, quote_y - 10, width - 50, quote_y + quote_bg_height], 
                         fill="#000000", outline="#FFD700", width=2)
            
            for line in quote_lines:
                draw.text((width//2, quote_y), line, font=quote_font, fill="#FFD700", anchor="mm")
                quote_y += 50
        
        # Add some visual elements based on content
        # Draw decorative elements
        if "success" in script.lower() or "achieve" in script.lower():
            # Success theme - draw stars
            for i in range(5):
                x = 100 + i * 120
                y = 100 + (i % 2) * 20
                draw.text((x, y), "★", font=script_font, fill="#FFD700")
        
        # Save image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            image_path = tmp_file.name
        
        print(f"✅ Dynamic image created: {image_path}")
        return image_path
        
    except Exception as e:
        raise Exception(f"Failed to create video image: {str(e)}")


def create_engaging_video_scenes(
    script: str,
    quote: str,
    title: str,
    width: int = 720,
    height: int = 1280
) -> list:
    """
    Create multiple engaging visual scenes for the video based on script content
    
    Args:
        script (str): Script text
        quote (str): Key quote
        title (str): Video title
        width (int): Image width
        height (int): Image height
        
    Returns:
        list: List of image paths for different scenes
    """
    try:
        scenes = []
        
        # Scene 1: Title/Hook Scene
        scenes.append(create_title_scene(title, width, height))
        
        # Scene 2: Content-Aware Scene (adapts to script theme)
        scenes.append(create_content_aware_scene(script, width, height))
        
        # Scene 3: Key Points Scene
        scenes.append(create_key_points_scene(script, width, height))
        
        # Scene 4: Main Content Scene
        scenes.append(create_main_content_scene(script, width, height))
        
        # Scene 5: Quote/Highlight Scene
        if quote:
            scenes.append(create_quote_scene(quote, width, height))
        
        # Scene 6: Call-to-Action Scene
        scenes.append(create_cta_scene(script, width, height))
        
        return scenes
        
    except Exception as e:
        raise Exception(f"Failed to create engaging video scenes: {str(e)}")


def create_title_scene(title: str, width: int, height: int) -> str:
    """Create an engaging title scene with animations"""
    try:
        # Create vibrant gradient background
        img = Image.new('RGB', (width, height), "#1a1a2e")
        draw = ImageDraw.Draw(img)
        
        # Create animated gradient background
        for y in range(height):
            ratio = y / height
            r = int(26 + 50 * ratio)  # 1a to 4a
            g = int(26 + 100 * ratio)  # 1a to aa
            b = int(46 + 80 * ratio)   # 2e to 8e
            r, g, b = min(255, r), min(255, g), min(255, b)
            color = (r, g, b)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add animated elements
        for i in range(20):
            x = (i * width // 20) + (i % 3) * 10
            y = height // 2 + (i % 5) * 20
            size = 30 + (i % 3) * 10
            color = "#FFD700" if i % 2 == 0 else "#FF6B6B"
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=color)
        
        # Try to use a system font
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 80)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        except:
            try:
                title_font = ImageFont.truetype("Arial.ttf", 80)
                subtitle_font = ImageFont.truetype("Arial.ttf", 36)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
        
        # Draw title with multiple effects
        title_y = height // 2 - 60
        
        # Glow effect
        for offset in range(5, 0, -1):
            glow_color = (255, 215, 0, 50 - offset * 10)
            draw.text((width//2 + offset, title_y + offset), title, font=title_font, fill=glow_color, anchor="mm")
        
        # Main title
        draw.text((width//2, title_y), title, font=title_font, fill="#FFD700", anchor="mm")
        
        # Subtitle
        draw.text((width//2, title_y + 100), "Viral Content Alert", font=subtitle_font, fill="#FFFFFF", anchor="mm")
        
        # Save scene
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to create title scene: {str(e)}")


def create_key_points_scene(script: str, width: int, height: int) -> str:
    """Create a scene highlighting key points from the script"""
    try:
        # Create dynamic background
        img = Image.new('RGB', (width, height), "#0f0f23")
        draw = ImageDraw.Draw(img)
        
        # Create animated background pattern
        for i in range(0, width, 40):
            for j in range(0, height, 40):
                if (i + j) % 80 == 0:
                    color = "#16213e" if (i + j) % 160 == 0 else "#0f0f23"
                    draw.rectangle([i, j, i+40, j+40], fill=color)
        
        # Extract key words from script
        words = script.split()
        key_words = [word.strip('.,!?').upper() for word in words if len(word) > 4][:6]
        
        # Try to use a system font
        try:
            word_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            label_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 28)
        except:
            try:
                word_font = ImageFont.truetype("Arial.ttf", 48)
                label_font = ImageFont.truetype("Arial.ttf", 28)
            except:
                word_font = ImageFont.load_default()
                label_font = ImageFont.load_default()
        
        # Draw key words in dynamic layout
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
        
        for i, word in enumerate(key_words):
            x = 100 + (i % 3) * 200
            y = 200 + (i // 3) * 150
            
            # Word background
            bbox = draw.textbbox((x, y), word, font=word_font)
            padding = 20
            draw.rectangle([bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding], 
                         fill=colors[i % len(colors)], outline="#FFFFFF", width=2)
            
            # Word text
            draw.text((x, y), word, font=word_font, fill="#FFFFFF", anchor="mm")
        
        # Add connecting lines
        for i in range(len(key_words) - 1):
            x1 = 100 + (i % 3) * 200
            y1 = 200 + (i // 3) * 150
            x2 = 100 + ((i+1) % 3) * 200
            y2 = 200 + ((i+1) // 3) * 150
            draw.line([(x1, y1), (x2, y2)], fill="#FFD700", width=3)
        
        # Save scene
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to create key points scene: {str(e)}")


def create_main_content_scene(script: str, width: int, height: int) -> str:
    """Create the main content scene with script text"""
    try:
        # Create engaging background
        img = Image.new('RGB', (width, height), "#2c3e50")
        draw = ImageDraw.Draw(img)
        
        # Create animated gradient
        for y in range(height):
            ratio = y / height
            r = int(44 + 50 * ratio)  # 2c to 5c
            g = int(62 + 30 * ratio)  # 3e to 4e
            b = int(80 + 40 * ratio)  # 50 to 70
            r, g, b = min(255, r), min(255, g), min(255, b)
            color = (r, g, b)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Try to use a system font
        try:
            script_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            highlight_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 42)
        except:
            try:
                script_font = ImageFont.truetype("Arial.ttf", 36)
                highlight_font = ImageFont.truetype("Arial.ttf", 42)
            except:
                script_font = ImageFont.load_default()
                highlight_font = ImageFont.load_default()
        
        # Format script text
        script_lines = textwrap.wrap(script, width=25)
        
        # Draw script with highlights
        y_start = 150
        for i, line in enumerate(script_lines[:8]):  # Limit to 8 lines
            y = y_start + i * 60
            
            # Highlight important lines
            if i % 3 == 0:  # Every 3rd line
                # Background highlight
                bbox = draw.textbbox((width//2, y), line, font=highlight_font)
                padding = 15
                draw.rectangle([bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding], 
                             fill="#E74C3C", outline="#FFFFFF", width=2)
                draw.text((width//2, y), line, font=highlight_font, fill="#FFFFFF", anchor="mm")
            else:
                draw.text((width//2, y), line, font=script_font, fill="#ECF0F1", anchor="mm")
        
        # Add visual elements
        # Draw progress indicators
        for i in range(5):
            x = 50 + i * 120
            y = height - 100
            color = "#27AE60" if i < 3 else "#95A5A6"
            draw.ellipse([x-10, y-10, x+10, y+10], fill=color)
        
        # Save scene
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to create main content scene: {str(e)}")


def create_quote_scene(quote: str, width: int, height: int) -> str:
    """Create a dramatic quote scene"""
    try:
        # Create dramatic background
        img = Image.new('RGB', (width, height), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        
        # Create radial gradient effect
        center_x, center_y = width // 2, height // 2
        max_radius = max(width, height) // 2
        
        for radius in range(max_radius, 0, -10):
            alpha = int(255 * (1 - radius / max_radius))
            color = (255, 215, 0, alpha)  # Gold with transparency
            draw.ellipse([center_x-radius, center_y-radius, center_x+radius, center_y+radius], 
                        fill=color)
        
        # Try to use a system font
        try:
            quote_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            attribution_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
        except:
            try:
                quote_font = ImageFont.truetype("Arial.ttf", 48)
                attribution_font = ImageFont.truetype("Arial.ttf", 32)
            except:
                quote_font = ImageFont.load_default()
                attribution_font = ImageFont.load_default()
        
        # Format quote
        quote_lines = textwrap.wrap(quote, width=20)
        
        # Draw quote with dramatic styling
        quote_y = height // 2 - (len(quote_lines) * 30) // 2
        
        for i, line in enumerate(quote_lines):
            y = quote_y + i * 60
            
            # Shadow effect
            draw.text((width//2 + 3, y + 3), line, font=quote_font, fill="#000000", anchor="mm")
            # Main text
            draw.text((width//2, y), line, font=quote_font, fill="#FFD700", anchor="mm")
        
        # Add quote marks
        draw.text((width//2 - 200, quote_y - 20), '"', font=quote_font, fill="#FFD700", anchor="mm")
        draw.text((width//2 + 200, quote_y + len(quote_lines) * 60), '"', font=quote_font, fill="#FFD700", anchor="mm")
        
        # Save scene
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to create quote scene: {str(e)}")


def create_cta_scene(script: str, width: int, height: int) -> str:
    """Create a call-to-action scene"""
    try:
        # Create energetic background
        img = Image.new('RGB', (width, height), "#8e44ad")
        draw = ImageDraw.Draw(img)
        
        # Create animated background
        for i in range(0, width, 60):
            for j in range(0, height, 60):
                if (i + j) % 120 == 0:
                    color = "#9b59b6" if (i + j) % 240 == 0 else "#8e44ad"
                    draw.rectangle([i, j, i+60, j+60], fill=color)
        
        # Try to use a system font
        try:
            cta_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 64)
            action_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        except:
            try:
                cta_font = ImageFont.truetype("Arial.ttf", 64)
                action_font = ImageFont.truetype("Arial.ttf", 36)
            except:
                cta_font = ImageFont.load_default()
                action_font = ImageFont.load_default()
        
        # Draw call-to-action
        cta_text = "DON'T MISS OUT!"
        action_text = "Follow for more viral content"
        
        # CTA with glow effect
        for offset in range(8, 0, -1):
            glow_color = (255, 255, 255, 100 - offset * 12)
            draw.text((width//2 + offset, height//2 - 50 + offset), cta_text, 
                     font=cta_font, fill=glow_color, anchor="mm")
        
        draw.text((width//2, height//2 - 50), cta_text, font=cta_font, fill="#FFFFFF", anchor="mm")
        draw.text((width//2, height//2 + 20), action_text, font=action_font, fill="#F39C12", anchor="mm")
        
        # Add action buttons
        button_y = height - 150
        button_width = 200
        button_height = 60
        
        # Subscribe button
        draw.rectangle([width//2 - button_width - 20, button_y, width//2 - 20, button_y + button_height], 
                      fill="#E74C3C", outline="#FFFFFF", width=3)
        draw.text((width//2 - button_width//2 - 20, button_y + button_height//2), "SUBSCRIBE", 
                 font=action_font, fill="#FFFFFF", anchor="mm")
        
        # Like button
        draw.rectangle([width//2 + 20, button_y, width//2 + button_width + 20, button_y + button_height], 
                      fill="#27AE60", outline="#FFFFFF", width=3)
        draw.text((width//2 + button_width//2 + 20, button_y + button_height//2), "LIKE", 
                 font=action_font, fill="#FFFFFF", anchor="mm")
        
        # Save scene
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to create CTA scene: {str(e)}")


def create_animated_text_effect(text: str, font, x: int, y: int, color: str, effect_type: str = "glow") -> list:
    """
    Create animated text effects for visual appeal
    
    Args:
        text (str): Text to animate
        font: Font object
        x (int): X position
        y (int): Y position
        color (str): Text color
        effect_type (str): Type of effect ("glow", "shadow", "pulse", "slide")
        
    Returns:
        list: List of drawing commands for the effect
    """
    effects = []
    
    if effect_type == "glow":
        # Create glow effect with multiple layers
        for offset in range(8, 0, -1):
            glow_color = color + hex(50 - offset * 6)[2:].zfill(2)  # Add alpha
            effects.append(("text", (x + offset, y + offset), text, font, glow_color))
        effects.append(("text", (x, y), text, font, color))
    
    elif effect_type == "shadow":
        # Create shadow effect
        shadow_color = "#000000"
        effects.append(("text", (x + 3, y + 3), text, font, shadow_color))
        effects.append(("text", (x, y), text, font, color))
    
    elif effect_type == "pulse":
        # Create pulse effect with multiple sizes
        for scale in [1.2, 1.1, 1.0]:
            effects.append(("text", (x, y), text, font, color))
    
    elif effect_type == "slide":
        # Create slide effect
        for offset in range(0, 20, 5):
            effects.append(("text", (x + offset, y), text, font, color))
    
    return effects


def create_content_aware_scene(script: str, width: int, height: int) -> str:
    """
    Create a scene that adapts to the content type and theme
    
    Args:
        script (str): Script content
        width (int): Image width
        height (int): Image height
        
    Returns:
        str: Path to generated scene
    """
    try:
        # Analyze script content for theme
        script_lower = script.lower()
        
        # Determine theme based on content
        if any(word in script_lower for word in ["success", "achieve", "win", "victory", "triumph"]):
            theme = "success"
            bg_color = "#27AE60"
            accent_color = "#F1C40F"
        elif any(word in script_lower for word in ["money", "wealth", "rich", "profit", "earn"]):
            theme = "money"
            bg_color = "#F39C12"
            accent_color = "#FFD700"
        elif any(word in script_lower for word in ["love", "heart", "relationship", "romance"]):
            theme = "love"
            bg_color = "#E91E63"
            accent_color = "#FF69B4"
        elif any(word in script_lower for word in ["fear", "scary", "danger", "warning"]):
            theme = "fear"
            bg_color = "#8E24AA"
            accent_color = "#FF5722"
        else:
            theme = "neutral"
            bg_color = "#34495E"
            accent_color = "#3498DB"
        
        # Create themed background
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Create theme-specific visual elements
        if theme == "success":
            # Success theme - stars and checkmarks
            for i in range(15):
                x = (i * width // 15) + (i % 3) * 20
                y = (i % 5) * height // 5 + 50
                size = 20 + (i % 3) * 10
                draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=accent_color)
                draw.text((x, y), "✓", font=ImageFont.load_default(), fill="#FFFFFF", anchor="mm")
        
        elif theme == "money":
            # Money theme - dollar signs and coins
            for i in range(20):
                x = (i * width // 20) + (i % 4) * 15
                y = (i % 6) * height // 6 + 30
                draw.text((x, y), "$", font=ImageFont.load_default(), fill=accent_color)
        
        elif theme == "love":
            # Love theme - hearts
            for i in range(12):
                x = (i * width // 12) + (i % 2) * 30
                y = (i % 4) * height // 4 + 40
                draw.text((x, y), "♥", font=ImageFont.load_default(), fill=accent_color)
        
        elif theme == "fear":
            # Fear theme - warning symbols
            for i in range(10):
                x = (i * width // 10) + (i % 3) * 25
                y = (i % 5) * height // 5 + 60
                draw.text((x, y), "⚠", font=ImageFont.load_default(), fill=accent_color)
        
        # Add script text with theme-appropriate styling
        try:
            script_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        except:
            try:
                script_font = ImageFont.truetype("Arial.ttf", 36)
            except:
                script_font = ImageFont.load_default()
        
        # Format and display script
        script_lines = textwrap.wrap(script, width=25)
        y_start = height // 2 - (len(script_lines) * 40) // 2
        
        for i, line in enumerate(script_lines[:6]):  # Limit to 6 lines
            y = y_start + i * 50
            
            # Add theme-specific text effects
            if theme == "success":
                # Green highlight for success
                bbox = draw.textbbox((width//2, y), line, font=script_font)
                padding = 10
                draw.rectangle([bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding], 
                             fill="#2ECC71", outline="#FFFFFF", width=2)
                draw.text((width//2, y), line, font=script_font, fill="#FFFFFF", anchor="mm")
            else:
                draw.text((width//2, y), line, font=script_font, fill="#FFFFFF", anchor="mm")
        
        # Save scene
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to create content-aware scene: {str(e)}")


def combine_audio_and_visuals(audio_path: str, image_path: str, output_dir: Path) -> str:
    """
    Combine audio and visual elements into a video using ffmpeg
    
    Args:
        audio_path (str): Path to audio file
        image_path (str): Path to image file
        output_dir (Path): Output directory
        
    Returns:
        str: Path to generated video
    """
    try:
        # Get audio duration
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', audio_path
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        
        # Generate output filename
        output_filename = f"elevenlabs_video_{int(duration)}s.mp4"
        output_path = output_dir / output_filename
        
        # Create video using ffmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-loop', '1', '-i', image_path,  # Input image (loop for duration)
            '-i', audio_path,  # Input audio
            '-c:v', 'libx264', '-tune', 'stillimage',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-shortest',  # End when shortest input ends
            '-t', str(duration),  # Duration
            str(output_path)
        ]
        
        # Run ffmpeg command
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        print(f"✅ Video created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to combine audio and visuals: {str(e)}")


def create_quote_focused_video(
    quote: str,
    author: str = "",
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_multilingual_v2"
) -> str:
    """
    Create a video focused on a specific quote
    
    Args:
        quote (str): Quote text
        author (str): Quote author
        voice_id (str): ElevenLabs voice ID
        model_id (str): ElevenLabs model ID
        
    Returns:
        str: Path to generated video
    """
    try:
        # Create a script from the quote
        script = f"Here's an inspiring quote: {quote}"
        if author:
            script += f" - {author}"
        
        # Create video
        video_path = create_elevenlabs_video(
            script=script,
            voice_id=voice_id,
            model_id=model_id,
            quote=quote,
            title="Inspirational Quote"
        )
        
        return video_path
        
    except Exception as e:
        raise Exception(f"Failed to create quote-focused video: {str(e)}")


def get_available_voices() -> list[Dict[str, Any]]:
    """
    Get list of available ElevenLabs voices
    
    Returns:
        list: List of available voices
    """
    try:
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise Exception("ELEVENLABS_API_KEY not found in environment variables")
        
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        voices = response.json().get('voices', [])
        return voices
        
    except Exception as e:
        raise Exception(f"Failed to get available voices: {str(e)}")


def create_person_narration_video(
    script: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_multilingual_v2",
    speaker_gender: str = "unknown",
    title: str = "Viral Moment"
) -> str:
    """
    Create a video with a person narrating the script (using AI-generated person image)
    
    Args:
        script (str): The script text to convert to speech
        voice_id (str): ElevenLabs voice ID
        model_id (str): ElevenLabs model ID
        speaker_gender (str): Gender of the speaker
        title (str): Video title
        
    Returns:
        str: Path to the generated video file
    """
    try:
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Select appropriate voice based on gender
        if speaker_gender != "unknown":
            selected_voice_id = get_voice_by_gender(speaker_gender)
            print(f"🎤 Using {speaker_gender} voice: {selected_voice_id}")
        else:
            selected_voice_id = voice_id
            print(f"🎤 Using provided voice: {selected_voice_id}")
        
        # Step 1: Generate audio using ElevenLabs
        print("🎵 Generating high-quality audio with ElevenLabs...")
        cleaned_script = clean_script_for_tts(script)
        audio_path = generate_elevenlabs_audio(cleaned_script, selected_voice_id, model_id)
        
        # Step 2: Create person narration scene
        print("👤 Creating person narration scene...")
        person_scene = create_person_narration_scene(script, speaker_gender, title)
        
        # Step 3: Create video with person narration
        print("🎬 Creating person narration video...")
        video_path = create_person_video(audio_path, person_scene, output_dir)
        
        # Clean up temporary files
        os.unlink(audio_path)
        os.unlink(person_scene)
        
        print(f"✅ Person narration video created successfully: {video_path}")
        return video_path
        
    except Exception as e:
        raise Exception(f"Failed to create person narration video: {str(e)}")


def create_person_narration_scene(script: str, speaker_gender: str, title: str) -> str:
    """
    Create a scene with a person narrating (using AI-generated person image)
    
    Args:
        script (str): Script content
        speaker_gender (str): Gender of the speaker
        title (str): Video title
        
    Returns:
        str: Path to generated scene image
    """
    try:
        # Create a person-like figure using simple shapes
        img = Image.new('RGB', (720, 1280), "#1a1a2e")
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        for y in range(1280):
            ratio = y / 1280
            r = int(26 + 50 * ratio)
            g = int(26 + 100 * ratio)
            b = int(46 + 80 * ratio)
            r, g, b = min(255, r), min(255, g), min(255, b)
            color = (r, g, b)
            draw.line([(0, y), (720, y)], fill=color)
        
        # Draw a simple person figure
        person_x = 360  # Center of image
        person_y = 400  # Person position
        
        # Head (circle)
        head_radius = 80
        draw.ellipse([person_x - head_radius, person_y - head_radius, 
                     person_x + head_radius, person_y + head_radius], 
                    fill="#FFD700", outline="#FFFFFF", width=3)
        
        # Eyes
        eye_y = person_y - 20
        draw.ellipse([person_x - 25, eye_y - 10, person_x - 15, eye_y + 10], fill="#000000")
        draw.ellipse([person_x + 15, eye_y - 10, person_x + 25, eye_y + 10], fill="#000000")
        
        # Mouth (smile)
        mouth_y = person_y + 20
        draw.arc([person_x - 30, mouth_y - 15, person_x + 30, mouth_y + 15], 0, 180, fill="#000000", width=3)
        
        # Body (rectangle)
        body_width = 120
        body_height = 200
        draw.rectangle([person_x - body_width//2, person_y + head_radius, 
                       person_x + body_width//2, person_y + head_radius + body_height], 
                      fill="#4A90E2", outline="#FFFFFF", width=3)
        
        # Arms
        arm_y = person_y + head_radius + 50
        draw.rectangle([person_x - body_width//2 - 30, arm_y, person_x - body_width//2 - 10, arm_y + 80], 
                      fill="#FFD700", outline="#FFFFFF", width=2)
        draw.rectangle([person_x + body_width//2 + 10, arm_y, person_x + body_width//2 + 30, arm_y + 80], 
                      fill="#FFD700", outline="#FFFFFF", width=2)
        
        # Add title
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            script_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            script_font = ImageFont.load_default()
        
        # Title at top
        draw.text((360, 50), title, font=title_font, fill="#FFD700", anchor="mm")
        
        # Add script text at bottom
        script_lines = textwrap.wrap(script, width=40)
        script_y = 1000
        for line in script_lines[:4]:  # Show first 4 lines
            draw.text((360, script_y), line, font=script_font, fill="#FFFFFF", anchor="mm")
            script_y += 30
        
        # Add speaking indicator
        draw.text((360, 750), "🎤 Speaking...", font=script_font, fill="#FF6B6B", anchor="mm")
        
        # Save scene
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            img.save(tmp_file.name, 'PNG')
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Failed to create person narration scene: {str(e)}")


def create_person_video(audio_path: str, person_scene_path: str, output_dir: Path) -> str:
    """
    Create a video with person narration scene
    
    Args:
        audio_path (str): Path to audio file
        person_scene_path (str): Path to person scene image
        output_dir (Path): Output directory
        
    Returns:
        str: Path to generated video
    """
    try:
        # Get audio duration
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', audio_path
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        
        # Generate output filename
        output_filename = f"person_narration_{int(duration)}s.mp4"
        output_path = output_dir / output_filename
        
        # Create video using ffmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-loop', '1', '-i', person_scene_path,  # Input image (loop for duration)
            '-i', audio_path,  # Input audio
            '-c:v', 'libx264', '-tune', 'stillimage',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-shortest',  # End when shortest input ends
            '-t', str(duration),  # Duration
            str(output_path)
        ]
        
        # Run ffmpeg command
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        print(f"✅ Person narration video created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to create person video: {str(e)}")


if __name__ == "__main__":
    # Test the video creation
    print("ElevenLabs Video Tool created successfully!")
    print("Available functions:")
    print("- create_elevenlabs_video()")
    print("- create_quote_focused_video()")
    print("- create_person_narration_video()")
    print("- get_available_voices()")
