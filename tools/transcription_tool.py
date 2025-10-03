"""
Transcription Tool - Transcribe audio files using local OpenAI Whisper
"""

import os
import whisper
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text using local OpenAI Whisper model
    
    Args:
        audio_path (str): Path to the audio file to transcribe
        
    Returns:
        str: Full text transcript
        
    Raises:
        Exception: If transcription fails or file doesn't exist
    """
    try:
        # Check if audio file exists
        if not os.path.exists(audio_path):
            raise Exception(f"Audio file not found: {audio_path}")
        
        # Get model size from environment (default: base)
        model_size = os.getenv('WHISPER_MODEL', 'base')
        
        print(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        print(f"Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path)
        
        transcript = result["text"].strip()
        
        if not transcript:
            raise Exception("No speech detected in audio file")
        
        print(f"Transcription completed. Length: {len(transcript)} characters")
        return transcript
        
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}")


def transcribe_with_timestamps(audio_path: str) -> dict:
    """
    Transcribe audio file with word-level timestamps
    
    Args:
        audio_path (str): Path to the audio file to transcribe
        
    Returns:
        dict: Transcript with segments and timestamps
    """
    try:
        if not os.path.exists(audio_path):
            raise Exception(f"Audio file not found: {audio_path}")
        
        model_size = os.getenv('WHISPER_MODEL', 'base')
        model = whisper.load_model(model_size)
        
        print(f"Transcribing with timestamps: {audio_path}")
        result = model.transcribe(audio_path, word_timestamps=True)
        
        return {
            'text': result["text"].strip(),
            'segments': result.get("segments", []),
            'language': result.get("language", "unknown")
        }
        
    except Exception as e:
        raise Exception(f"Failed to transcribe with timestamps: {str(e)}")


def get_audio_duration(audio_path: str) -> float:
    """
    Get the duration of an audio file in seconds
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        import librosa
        duration = librosa.get_duration(filename=audio_path)
        return duration
    except Exception as e:
        print(f"Warning: Could not get audio duration: {e}")
        return 0.0


if __name__ == "__main__":
    # Test the function
    test_audio = "test_audio.mp3"  # Replace with actual test file
    if os.path.exists(test_audio):
        try:
            transcript = transcribe_audio(test_audio)
            print(f"Test successful. Transcript: {transcript[:100]}...")
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("No test audio file found. Please provide a valid audio file for testing.")
