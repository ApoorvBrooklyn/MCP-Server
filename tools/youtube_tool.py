"""
YouTube Tool - Download audio from YouTube videos using yt-dlp
"""

import os
import yt_dlp
from pathlib import Path
from typing import Optional


def get_audio_from_youtube(url: str) -> str:
    """
    Download audio from a YouTube video URL using yt-dlp
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Path to the downloaded audio file
        
    Raises:
        Exception: If download fails or URL is invalid
    """
    try:
        # Create downloads directory if it doesn't exist
        downloads_dir = Path("downloads")
        downloads_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options for audio-only download
        ydl_opts = {
            'format': 'bestaudio/best',  # Best audio quality
            'outtmpl': str(downloads_dir / '%(title)s.%(ext)s'),  # Output template
            'extractaudio': True,  # Extract audio
            'audioformat': 'mp3',  # Convert to MP3
            'audioquality': '192K',  # Audio quality
            'noplaylist': True,  # Don't download playlists
            'quiet': True,  # Suppress output
            'no_warnings': True,  # Suppress warnings
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info first to get the filename
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'unknown')
            
            # Clean filename for filesystem
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:100]  # Limit length
            
            # Update output template with safe title
            ydl_opts['outtmpl'] = str(downloads_dir / f'{safe_title}.%(ext)s')
            
            # Download the audio
            ydl.download([url])
            
            # Find the downloaded file
            audio_files = list(downloads_dir.glob(f"{safe_title}.*"))
            if audio_files:
                audio_path = str(audio_files[0])
                print(f"Successfully downloaded audio: {audio_path}")
                return audio_path
            else:
                raise Exception("Audio file not found after download")
                
    except yt_dlp.DownloadError as e:
        if "Video unavailable" in str(e):
            raise Exception(f"Video is unavailable or private: {url}")
        elif "Sign in to confirm your age" in str(e):
            raise Exception(f"Video requires age verification: {url}")
        else:
            raise Exception(f"Download error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to download audio from {url}: {str(e)}")


def get_video_info(url: str) -> dict:
    """
    Get video information without downloading
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        dict: Video information including title, duration, etc.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', '')[:500] + '...' if info.get('description') else ''
            }
    except Exception as e:
        raise Exception(f"Failed to get video info: {str(e)}")


if __name__ == "__main__":
    # Test the function
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    try:
        audio_path = get_audio_from_youtube(test_url)
        print(f"Test successful: {audio_path}")
    except Exception as e:
        print(f"Test failed: {e}")
