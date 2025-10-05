"""
Video Tool - Create videos with voiceover and visual elements
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
# MoviePy is optional; only needed for text-based video generation helpers
try:
    import moviepy.editor as mp
except Exception:
    mp = None  # Lazily required by functions that use MoviePy
import textwrap


def _get_audio_duration_seconds(audio_path: str) -> float:
    duration_cmd = [
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', audio_path
    ]
    result = subprocess.run(duration_cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def create_looped_video_with_audio(
    voiceover_path: str,
    background_video_path: str,
    output_path: str | None = None,
    fps: int = 30,
    crf: int = 20,
    preset: str = 'medium'
) -> str:
    """
    Loop a background video to match the voiceover duration and replace its audio.
    """
    try:
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)

        duration = _get_audio_duration_seconds(voiceover_path)
        if duration <= 0:
            raise Exception("Could not determine audio duration")

        if output_path is None:
            output_path = output_dir / f"loop_video_{int(duration)}s.mp4"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use stream_loop to repeat video frames, trim to duration, and map audio from voiceover
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1', '-i', background_video_path,
            '-i', voiceover_path,
            '-t', str(duration),
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', str(fps), '-crf', str(crf), '-preset', preset,
            '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")

        return str(output_path)
    except Exception as e:
        raise Exception(f"Failed to create looped video: {str(e)}")


def create_sample_loop_video_from_script(script_text: str, background_video: str = "Sample_Video.mp4") -> str:
    """
    Generate ElevenLabs audio from script and loop Sample_Video.mp4 to its duration.
    """
    # Use existing ElevenLabs integration for high-quality narration
    from tools.voice_tool import create_high_quality_voiceover
    audio_path = create_high_quality_voiceover(script_text)
    return create_looped_video_with_audio(audio_path, background_video_path=background_video)


def create_video_with_voiceover(
    voiceover_path: str,
    script: str,
    quote: str = "",
    background_color: str = "#000000",
    text_color: str = "#FFFFFF",
    duration: Optional[float] = None
) -> str:
    """
    Create a video with voiceover and visual text elements using ffmpeg
    
    Args:
        voiceover_path (str): Path to the voiceover audio file
        script (str): The script text to display
        quote (str): Key quote to highlight
        background_color (str): Background color (hex format)
        text_color (str): Text color (hex format)
        duration (float, optional): Video duration (if None, uses audio duration)
        
    Returns:
        str: Path to the generated video file
    """
    try:
        if mp is None:
            raise Exception("moviepy is required for create_video_with_voiceover. Install with: pip install moviepy")
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Get audio duration using ffprobe
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', voiceover_path
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        video_duration = duration or float(result.stdout.strip())
        
        # Create video dimensions (9:16 aspect ratio for mobile)
        width, height = 720, 1280
        
        # Create a simple text image
        text_image_path = create_text_image(script, quote, width, height, background_color, text_color)
        
        # Generate output filename
        output_filename = f"viral_video_{int(video_duration)}s.mp4"
        output_path = output_dir / output_filename
        
        # Create video using ffmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-loop', '1', '-i', text_image_path,  # Input image (loop for duration)
            '-i', voiceover_path,  # Input audio
            '-c:v', 'libx264', '-tune', 'stillimage',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-b:a', '192k',  # Audio bitrate
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-shortest',  # End when shortest input ends
            '-t', str(video_duration),  # Duration
            str(output_path)
        ]
        
        # Run ffmpeg command
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        # Clean up temporary image
        os.unlink(text_image_path)
        
        print(f"Video created successfully: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to create video: {str(e)}")


def create_text_image(
    script: str,
    quote: str,
    width: int,
    height: int,
    background_color: str,
    text_color: str
) -> str:
    """
    Create a simple PNG with wrapped script text and optional quote.
    Returns the temporary image path.
    """
    tmp_dir = Path("generated_images")
    tmp_dir.mkdir(exist_ok=True)
    img_path = tmp_dir / "text_frame.png"

    # Basic font fallback (system default)
    try:
        font_title = ImageFont.truetype("Arial.ttf", 40)
        font_body = ImageFont.truetype("Arial.ttf", 32)
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    img = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(img)

    margin = 40
    y = margin
    max_text_width = width - margin * 2

    def draw_wrapped(text: str, font: ImageFont.ImageFont, y_pos: int, fill: str) -> int:
        wrapped = []
        line = ""
        for word in text.split():
            test = (line + " " + word).strip()
            w, _ = draw.textsize(test, font=font)
            if w <= max_text_width:
                line = test
            else:
                if line:
                    wrapped.append(line)
                line = word
        if line:
            wrapped.append(line)
        for l in wrapped:
            draw.text((margin, y_pos), l, font=font, fill=fill)
            y_pos += int(font.size * 1.4)
        return y_pos

    # Title
    y = draw_wrapped("Narration", font_title, y, text_color)
    y += 10

    # Body
    y = draw_wrapped(script, font_body, y, text_color)

    # Quote
    if quote:
        y += 20
        y = draw_wrapped(f'"{quote}"', font_title, y, "#FFD700")

    img.save(img_path)
    return str(img_path)


def create_text_clips(
    script: str,
    quote: str,
    width: int,
    height: int,
    text_color: str,
    duration: float
) -> List[Any]:
    """
    Create text clips for the video
    
    Args:
        script (str): Script text
        quote (str): Key quote to highlight
        width (int): Video width
        height (int): Video height
        text_color (str): Text color
        duration (float): Video duration
        
    Returns:
        List[mp.TextClip]: List of text clips
    """
    if mp is None:
        raise Exception("moviepy is required for create_text_clips. Install with: pip install moviepy")
    clips = []
    
    # Split script into segments for different timing
    script_segments = parse_script_segments(script)
    
    current_time = 0
    
    for i, segment in enumerate(script_segments):
        if current_time >= duration:
            break
            
        # Create text clip
        text_clip = mp.TextClip(
            segment['text'],
            fontsize=48,
            color=text_color,
            font='Arial-Bold',
            method='caption',
            size=(width - 100, None)
        ).set_position('center').set_start(current_time)
        
        # Set duration for this segment
        segment_duration = min(segment.get('duration', 3), duration - current_time)
        text_clip = text_clip.set_duration(segment_duration)
        
        # Add fade effects
        text_clip = text_clip.fadein(0.5).fadeout(0.5)
        
        clips.append(text_clip)
        current_time += segment_duration
    
    # Add quote highlight if provided
    if quote and current_time < duration:
        quote_clip = mp.TextClip(
            f'"{quote}"',
            fontsize=56,
            color='#FFD700',  # Gold color for quote
            font='Arial-Bold',
            method='caption',
            size=(width - 50, None)
        ).set_position('center').set_start(current_time)
        
        quote_duration = min(4, duration - current_time)
        quote_clip = quote_clip.set_duration(quote_duration).fadein(0.5).fadeout(0.5)
        clips.append(quote_clip)
    
    return clips


def parse_script_segments(script: str) -> List[Dict[str, Any]]:
    """
    Parse script into timed segments
    
    Args:
        script (str): Script text with timing information
        
    Returns:
        List[Dict]: List of script segments with timing
    """
    segments = []
    lines = script.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for timing patterns like [0-3s], [3-15s], etc.
        if '[' in line and ']' in line:
            # Extract timing information
            start_bracket = line.find('[')
            end_bracket = line.find(']')
            timing = line[start_bracket+1:end_bracket]
            
            # Extract text after timing
            text = line[end_bracket+1:].strip()
            if text.startswith(':'):
                text = text[1:].strip()
            
            # Parse duration from timing
            duration = 3  # Default duration
            if '-' in timing and 's' in timing:
                try:
                    end_time = timing.split('-')[1].replace('s', '')
                    start_time = timing.split('-')[0].replace('s', '')
                    duration = float(end_time) - float(start_time)
                except:
                    duration = 3
            
            segments.append({
                'text': text,
                'duration': duration
            })
        else:
            # No timing info, use default duration
            segments.append({
                'text': line,
                'duration': 3
            })
    
    return segments


def create_simple_video(
    voiceover_path: str,
    title: str,
    subtitle: str = "",
    background_color: str = "#1a1a1a",
    text_color: str = "#FFFFFF"
) -> str:
    """
    Create a simple video with title and subtitle
    
    Args:
        voiceover_path (str): Path to voiceover audio
        title (str): Main title text
        subtitle (str): Subtitle text
        background_color (str): Background color
        text_color (str): Text color
        
    Returns:
        str: Path to generated video
    """
    try:
        if mp is None:
            raise Exception("moviepy is required for create_simple_video. Install with: pip install moviepy")
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Load audio
        audio_clip = mp.AudioFileClip(voiceover_path)
        duration = audio_clip.duration
        
        # Video dimensions (9:16 for mobile)
        width, height = 720, 1280
        
        # Create background
        background = mp.ColorClip(size=(width, height), color=background_color, duration=duration)
        
        # Create title clip
        title_clip = mp.TextClip(
            title,
            fontsize=64,
            color=text_color,
            font='Arial-Bold',
            method='caption',
            size=(width - 100, None)
        ).set_position('center').set_duration(duration)
        
        clips = [background, title_clip]
        
        # Add subtitle if provided
        if subtitle:
            subtitle_clip = mp.TextClip(
                subtitle,
                fontsize=36,
                color='#CCCCCC',
                font='Arial',
                method='caption',
                size=(width - 100, None)
            ).set_position(('center', height - 200)).set_duration(duration)
            clips.append(subtitle_clip)
        
        # Combine clips
        final_video = mp.CompositeVideoClip(clips)
        final_video = final_video.set_audio(audio_clip)
        
        # Output path
        output_filename = f"simple_video_{int(duration)}s.mp4"
        output_path = output_dir / output_filename
        
        # Write video
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac'
        )
        
        # Clean up
        audio_clip.close()
        final_video.close()
        
        print(f"Simple video created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to create simple video: {str(e)}")


def create_quote_video(
    voiceover_path: str,
    quote: str,
    author: str = "",
    background_color: str = "#000000",
    quote_color: str = "#FFFFFF",
    author_color: str = "#CCCCCC"
) -> str:
    """
    Create a video focused on a quote
    
    Args:
        voiceover_path (str): Path to voiceover audio
        quote (str): Quote text
        author (str): Author name
        background_color (str): Background color
        quote_color (str): Quote text color
        author_color (str): Author text color
        
    Returns:
        str: Path to generated video
    """
    try:
        if mp is None:
            raise Exception("moviepy is required for create_quote_video. Install with: pip install moviepy")
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Load audio
        audio_clip = mp.AudioFileClip(voiceover_path)
        duration = audio_clip.duration
        
        # Video dimensions
        width, height = 720, 1280
        
        # Create background
        background = mp.ColorClip(size=(width, height), color=background_color, duration=duration)
        
        # Create quote clip
        quote_clip = mp.TextClip(
            f'"{quote}"',
            fontsize=48,
            color=quote_color,
            font='Arial-Bold',
            method='caption',
            size=(width - 80, None),
            align='center'
        ).set_position('center').set_duration(duration)
        
        clips = [background, quote_clip]
        
        # Add author if provided
        if author:
            author_clip = mp.TextClip(
                f"— {author}",
                fontsize=32,
                color=author_color,
                font='Arial-Italic',
                method='caption',
                size=(width - 100, None)
            ).set_position(('center', height - 150)).set_duration(duration)
            clips.append(author_clip)
        
        # Combine clips
        final_video = mp.CompositeVideoClip(clips)
        final_video = final_video.set_audio(audio_clip)
        
        # Output path
        output_filename = f"quote_video_{int(duration)}s.mp4"
        output_path = output_dir / output_filename
        
        # Write video
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac'
        )
        
        # Clean up
        audio_clip.close()
        final_video.close()
        
        print(f"Quote video created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to create quote video: {str(e)}")


if __name__ == "__main__":
    # Test the video creation functions
    print("Video tool created successfully!")
    print("Available functions:")
    print("- create_video_with_voiceover()")
    print("- create_looped_video_with_audio()")
    print("- create_sample_loop_video_from_script()")
    print("- create_simple_video()")
    print("- create_quote_video()")
