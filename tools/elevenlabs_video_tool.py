"""
ElevenLabs Video Tool - Create professional videos using ElevenLabs TTS and visual elements
"""

import os
import tempfile
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import textwrap


def create_elevenlabs_video(
    script: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice ID
    model_id: str = "eleven_multilingual_v2",
    background_color: str = "#000000",
    text_color: str = "#FFFFFF",
    quote: str = "",
    title: str = "Viral Moment"
) -> str:
    """
    Create a professional video using ElevenLabs TTS and visual elements
    
    Args:
        script (str): The script text to convert to speech and display
        voice_id (str): ElevenLabs voice ID
        model_id (str): ElevenLabs model ID
        background_color (str): Background color (hex format)
        text_color (str): Text color (hex format)
        quote (str): Key quote to highlight
        title (str): Video title
        
    Returns:
        str: Path to the generated video file
    """
    try:
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Step 1: Generate audio using ElevenLabs
        print("🎵 Generating audio with ElevenLabs...")
        audio_path = generate_elevenlabs_audio(script, voice_id, model_id)
        
        # Step 2: Create visual elements
        print("🎨 Creating visual elements...")
        image_path = create_video_image(script, quote, title, background_color, text_color)
        
        # Step 3: Combine audio and visuals into video
        print("🎬 Creating video...")
        video_path = combine_audio_and_visuals(audio_path, image_path, output_dir)
        
        # Clean up temporary files
        os.unlink(audio_path)
        os.unlink(image_path)
        
        print(f"✅ Video created successfully: {video_path}")
        return video_path
        
    except Exception as e:
        raise Exception(f"Failed to create ElevenLabs video: {str(e)}")


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
                "stability": 0.5,
                "similarity_boost": 0.5,
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


if __name__ == "__main__":
    # Test the video creation
    print("ElevenLabs Video Tool created successfully!")
    print("Available functions:")
    print("- create_elevenlabs_video()")
    print("- create_quote_focused_video()")
    print("- get_available_voices()")
