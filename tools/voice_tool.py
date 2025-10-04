"""
Voice Tool - Generate voiceovers using local Coqui TTS
"""

import os
import tempfile
from pathlib import Path
from typing import Optional
from TTS.api import TTS
import torch


def create_voiceover(script_text: str, voice_model: str = None, speaker_gender: str = "unknown") -> str:
    """
    Generate voiceover audio from script text using local Coqui TTS
    
    Args:
        script_text (str): Script text to convert to voiceover
        voice_model (str): TTS model to use (if None, will auto-select based on gender)
        speaker_gender (str): Gender of the speaker ("male", "female", "unknown")
        
    Returns:
        str: Path to the generated audio file
        
    Raises:
        Exception: If voice generation fails
    """
    try:
        # Create output directory
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        # Select voice model based on gender if not specified
        if voice_model is None:
            if speaker_gender == "male":
                voice_model = "tts_models/en/vctk/vits"  # Male voice model
            elif speaker_gender == "female":
                voice_model = "tts_models/en/ljspeech/tacotron2-DDC"  # Female voice model
            else:
                voice_model = "tts_models/en/ljspeech/tacotron2-DDC"  # Default female voice
        
        print(f"Loading TTS model: {voice_model}")
        
        # Initialize TTS model
        tts = TTS(model_name=voice_model, progress_bar=True)
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        output_path = output_dir / f"voiceover_{timestamp}.wav"
        
        print(f"Generating voiceover for {len(script_text)} characters...")
        
        # Generate speech with speaker selection for multi-speaker models
        if "vctk" in voice_model:  # Multi-speaker model
            # Use a male speaker ID for VCTK model
            tts.tts_to_file(text=script_text, file_path=str(output_path), speaker="p225")
        else:
            tts.tts_to_file(text=script_text, file_path=str(output_path))
        
        print(f"Voiceover generated successfully: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to generate voiceover: {str(e)}")


def create_voiceover_with_emotion(script_text: str, emotion: str = "neutral") -> str:
    """
    Generate voiceover with specific emotion using Coqui TTS
    
    Args:
        script_text (str): Script text to convert to voiceover
        emotion (str): Emotion to convey (neutral, happy, sad, angry, excited)
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Map emotions to TTS parameters
        emotion_settings = {
            "neutral": {"speed": 1.0, "pitch": 1.0},
            "happy": {"speed": 1.1, "pitch": 1.1},
            "sad": {"speed": 0.9, "pitch": 0.9},
            "angry": {"speed": 1.2, "pitch": 1.0},
            "excited": {"speed": 1.3, "pitch": 1.2}
        }
        
        settings = emotion_settings.get(emotion, emotion_settings["neutral"])
        
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        # Use a model that supports emotion control
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True)
        
        import time
        timestamp = int(time.time())
        output_path = output_dir / f"voiceover_{emotion}_{timestamp}.wav"
        
        print(f"Generating {emotion} voiceover...")
        
        # Generate speech with emotion
        tts.tts_to_file(
            text=script_text, 
            file_path=str(output_path),
            speed=settings["speed"]
        )
        
        print(f"Emotional voiceover generated: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to generate emotional voiceover: {str(e)}")


def get_available_voices() -> list:
    """
    Get list of available TTS voices/models
    
    Returns:
        list: Available voice models
    """
    try:
        # List available models
        models = TTS.list_models()
        
        # Filter for English models
        english_models = [model for model in models if 'en' in model]
        
        return english_models
    except Exception as e:
        print(f"Warning: Could not list available voices: {e}")
        return ["tts_models/en/ljspeech/tacotron2-DDC"]


def create_multiple_voiceovers(script_text: str, voices: list = None) -> dict:
    """
    Create multiple voiceover versions with different voices
    
    Args:
        script_text (str): Script text to convert
        voices (list): List of voice models to use
        
    Returns:
        dict: Dictionary mapping voice names to file paths
    """
    try:
        if voices is None:
            voices = [
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/vctk/vits"
            ]
        
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        results = {}
        
        for voice in voices:
            try:
                print(f"Generating voiceover with {voice}...")
                
                tts = TTS(model_name=voice, progress_bar=True)
                
                import time
                timestamp = int(time.time())
                voice_name = voice.split('/')[-1]
                output_path = output_dir / f"voiceover_{voice_name}_{timestamp}.wav"
                
                tts.tts_to_file(text=script_text, file_path=str(output_path))
                
                results[voice_name] = str(output_path)
                print(f"Generated: {output_path}")
                
            except Exception as e:
                print(f"Failed to generate voiceover with {voice}: {e}")
                continue
        
        return results
        
    except Exception as e:
        raise Exception(f"Failed to create multiple voiceovers: {str(e)}")


def optimize_script_for_tts(script_text: str) -> str:
    """
    Optimize script text for better TTS pronunciation
    
    Args:
        script_text (str): Original script text
        
    Returns:
        str: Optimized script text
    """
    try:
        # Common TTS optimizations
        optimizations = {
            # Numbers
            "1st": "first",
            "2nd": "second", 
            "3rd": "third",
            "4th": "fourth",
            "5th": "fifth",
            "10th": "tenth",
            "100th": "hundredth",
            
            # Common abbreviations
            "Dr.": "Doctor",
            "Mr.": "Mister",
            "Mrs.": "Misses",
            "Prof.": "Professor",
            "etc.": "etcetera",
            "vs.": "versus",
            "&": "and",
            
            # Currency
            "$": "dollars",
            "€": "euros",
            "£": "pounds",
            
            # Time
            "AM": "A M",
            "PM": "P M",
            "EST": "Eastern Standard Time",
            "PST": "Pacific Standard Time",
        }
        
        optimized_text = script_text
        
        for old, new in optimizations.items():
            optimized_text = optimized_text.replace(old, new)
        
        # Add pauses for better pacing
        optimized_text = optimized_text.replace(".", ". ")
        optimized_text = optimized_text.replace("!", "! ")
        optimized_text = optimized_text.replace("?", "? ")
        
        return optimized_text.strip()
        
    except Exception as e:
        print(f"Warning: Could not optimize script: {e}")
        return script_text


def get_audio_duration(audio_path: str) -> float:
    """
    Get the duration of generated audio file
    
    Args:
        audio_path (str): Path to audio file
        
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
    test_script = "Hello! This is a test of the voice generation system. The quick brown fox jumps over the lazy dog."
    
    try:
        voiceover_path = create_voiceover(test_script)
        print(f"Test successful: {voiceover_path}")
        
        # Test emotional voiceover
        excited_voiceover = create_voiceover_with_emotion(test_script, "excited")
        print(f"Excited voiceover: {excited_voiceover}")
        
    except Exception as e:
        print(f"Test failed: {e}")
