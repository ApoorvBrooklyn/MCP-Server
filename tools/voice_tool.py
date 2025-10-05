"""
Voice Tool - Generate voiceovers using local Coqui TTS
"""

import os
import tempfile
import re
from pathlib import Path
from typing import Optional
from TTS.api import TTS
import torch


def enhance_script_for_natural_speech(script_text: str) -> str:
    """
    Enhance script text for natural, listenable speech with proper pacing and emphasis
    
    Args:
        script_text (str): Original script text
        
    Returns:
        str: Enhanced script text optimized for natural speech
    """
    # Start with the original script
    enhanced_script = script_text
    
    # Add natural pauses after sentences (not too long, not too short)
    enhanced_script = re.sub(r'\.(?!\s)', '. ', enhanced_script)
    enhanced_script = re.sub(r'!(?!\s)', '! ', enhanced_script)
    enhanced_script = re.sub(r'\?(?!\s)', '? ', enhanced_script)
    
    # Add subtle pauses for natural flow (not dramatic)
    enhanced_script = re.sub(r'\.\s+([A-Z])', '. \\1', enhanced_script)
    
    # Make exclamations more natural (not overly dramatic)
    enhanced_script = re.sub(r'!', '!', enhanced_script)
    
    # Add gentle emphasis to important words without being irritating
    important_words = ['amazing', 'incredible', 'unbelievable', 'shocking', 'surprising', 'wow', 'wait', 'listen', 'here']
    for word in important_words:
        # Add subtle emphasis, not dramatic pauses
        enhanced_script = re.sub(f'\\b{word}\\b', f'{word}', enhanced_script, flags=re.IGNORECASE)
    
    # Make numbers more natural to pronounce
    enhanced_script = re.sub(r'(\d+)%', r'\\1 percent', enhanced_script)
    enhanced_script = re.sub(r'(\d+)', r'\\1', enhanced_script)
    
    # Make questions flow naturally
    enhanced_script = re.sub(r'\?', '?', enhanced_script)
    
    # Add natural speech patterns
    # Replace "and" with "and" for better flow
    enhanced_script = re.sub(r'\band\b', 'and', enhanced_script)
    
    # Add natural connectors
    enhanced_script = re.sub(r'\.\s+([A-Z])', '. Now, \\1', enhanced_script)
    
    # Clean up multiple spaces but keep natural flow
    enhanced_script = re.sub(r'\s+', ' ', enhanced_script)
    
    # Remove any excessive punctuation that might sound robotic
    enhanced_script = re.sub(r'\.{3,}', '...', enhanced_script)
    enhanced_script = re.sub(r'!{2,}', '!', enhanced_script)
    enhanced_script = re.sub(r'\?{2,}', '?', enhanced_script)
    
    return enhanced_script.strip()


def create_natural_voiceover(script_text: str) -> str:
    """
    Generate natural, listenable voiceover using ElevenLabs with optimized settings
    
    Args:
        script_text (str): Script text to convert to voiceover
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        import requests
        import tempfile
        
        # Use a lighter, more natural voice (not too deep)
        voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella - Clear, engaging, lighter voice
        
        # Get API key from environment
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise Exception("ELEVENLABS_API_KEY not found in environment variables")
        
        # Create output directory
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Clean the script thoroughly to remove all problematic formatting
        cleaned_script = clean_script_for_tts(script_text)
        
        # Process entire script without truncation
        print(f"📝 Processing script of {len(cleaned_script)} characters")
        
        data = {
            "text": cleaned_script,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,  # Lower stability for more natural variation
                "similarity_boost": 0.6,  # Lower similarity for more natural sound
                "style": 0.4,  # Higher style for more engaging delivery
                "use_speaker_boost": True
            }
        }
        
        print(f"Generating natural, lighter voiceover...")
        
        # Make API request
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        output_path = output_dir / f"natural_voiceover_{timestamp}.wav"
        
        # Save audio to file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Natural voiceover generated successfully: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to generate natural voiceover: {str(e)}")


def clean_script_for_tts(script_text: str) -> str:
    """
    Clean script text to remove ALL formatting elements that make audio unbearable
    
    Args:
        script_text (str): Raw script text with formatting
        
    Returns:
        str: Cleaned script text ready for TTS
    """
    # Remove ALL asterisks and emphasis markers
    script_text = re.sub(r'\*+([^*]*)\*+', r'\1', script_text)  # Remove *text* or **text**
    script_text = re.sub(r'_{2,}([^_]*?)_{2,}', r'\1', script_text)  # Remove __text__
    script_text = re.sub(r'~+([^~]*?)~+', r'\1', script_text)  # Remove ~~text~~
    
    # Remove ALL brackets and their contents
    script_text = re.sub(r'\[[^\]]*\]', '', script_text)  # [like this]
    script_text = re.sub(r'\([^)]*\)', '', script_text)   # (like this)
    script_text = re.sub(r'\{[^}]*\}', '', script_text)   # {like this}
    
    # Remove ALL quotes and emphasis markers
    script_text = re.sub(r'"([^"]*)"', r'\1', script_text)  # "text"
    script_text = re.sub(r"'([^']*)'", r'\1', script_text)  # 'text'
    script_text = re.sub(r'`([^`]*)`', r'\1', script_text)  # `text`
    
    # Remove ALL punctuation that causes audio issues
    script_text = re.sub(r'\.{3,}', '.', script_text)  # Replace ... with .
    script_text = re.sub(r'!{2,}', '!', script_text)   # Replace !! with !
    script_text = re.sub(r'\?{2,}', '?', script_text)  # Replace ?? with ?
    script_text = re.sub(r'-{2,}', ' ', script_text)   # Replace -- with space
    
    # Remove standalone punctuation
    script_text = re.sub(r'^[.!?]+\s*$', '', script_text, flags=re.MULTILINE)
    
    # Remove special characters that cause audio issues
    script_text = re.sub(r'[#@$%^&+=|\\/<>]', '', script_text)
    
    # Clean up whitespace and line breaks
    script_text = re.sub(r'\s+', ' ', script_text)  # Multiple spaces to single space
    script_text = re.sub(r'\n\s*\n', '\n', script_text)  # Multiple newlines to single
    script_text = script_text.strip()
    
    # Remove empty lines
    lines = [line.strip() for line in script_text.split('\n') if line.strip()]
    script_text = '\n'.join(lines)
    
    # Final cleanup - remove any remaining problematic characters
    script_text = re.sub(r'[^\w\s.,!?]', '', script_text)
    
    return script_text


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
                voice_model = "tts_models/en/vctk/vits"  # Multi-speaker model with male voices
            elif speaker_gender == "female":
                voice_model = "tts_models/en/ljspeech/tacotron2-DDC"  # High-quality female voice
            else:
                voice_model = "tts_models/en/vctk/vits"  # Default to multi-speaker model
        
        print(f"Loading TTS model: {voice_model} for {speaker_gender} speaker")
        
        # Initialize TTS model
        tts = TTS(model_name=voice_model, progress_bar=True)
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        output_path = output_dir / f"voiceover_{speaker_gender}_{timestamp}.wav"
        
        # Clean the script text before TTS
        cleaned_script = clean_script_for_tts(script_text)
        print(f"Generating {speaker_gender} voiceover for {len(cleaned_script)} characters...")
        
        # Generate speech with speaker selection for multi-speaker models
        if "vctk" in voice_model:  # Multi-speaker model
            # Use appropriate speaker ID based on gender for better quality
            if speaker_gender == "male":
                speaker_id = "p225"  # High-quality male speaker
            elif speaker_gender == "female":
                speaker_id = "p226"  # High-quality female speaker
            else:
                speaker_id = "p225"  # Default to male speaker
            print(f"Using speaker ID: {speaker_id} for {speaker_gender} voice")
            tts.tts_to_file(text=cleaned_script, file_path=str(output_path), speaker=speaker_id)
        else:
            # For single-speaker models, use default settings
            tts.tts_to_file(text=cleaned_script, file_path=str(output_path))
        
        print(f"Voiceover generated successfully: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to generate voiceover: {str(e)}")


def create_high_quality_voiceover(script_text: str) -> str:
    """
    Generate high-quality voiceover using ElevenLabs with a single, professional narrator
    
    Args:
        script_text (str): Script text to convert to voiceover
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        import requests
        import tempfile
        
        # Use a single, high-quality professional narrator voice
        # This is a premium ElevenLabs voice optimized for narration
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Adam - Professional, clear narrator
        
        # Get API key from environment
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise Exception("ELEVENLABS_API_KEY not found in environment variables")
        
        # Create output directory
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Enhance the script for better TTS
        enhanced_script = enhance_script_for_tts(script_text)
        
        data = {
            "text": enhanced_script,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.8,  # High stability for consistent narration
                "similarity_boost": 0.8,  # High similarity for voice consistency
                "style": 0.2,  # Slight style for natural variation
                "use_speaker_boost": True
            }
        }
        
        print(f"Generating high-quality voiceover with professional narrator...")
        
        # Make API request
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        output_path = output_dir / f"high_quality_voiceover_{timestamp}.wav"
        
        # Save audio to file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"High-quality voiceover generated successfully: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to generate high-quality voiceover: {str(e)}")


def create_voiceover_with_elevenlabs(script_text: str, speaker_gender: str = "unknown") -> str:
    """
    Generate voiceover audio using ElevenLabs TTS with gender-appropriate voice
    
    Args:
        script_text (str): Script text to convert to voiceover
        speaker_gender (str): Gender of the speaker ("male", "female", "unknown")
        
    Returns:
        str: Path to the generated audio file
        
    Raises:
        Exception: If voice generation fails
    """
    try:
        import requests
        import tempfile
        
        # Voice ID mapping for different genders - using high-quality voices
        voice_mapping = {
            "male": "21m00Tcm4TlvDq8ikWAM",      # Adam - Deep, authoritative male voice
            "female": "EXAVITQu4vr4xnSDxMaL",    # Bella - Clear, engaging female voice  
            "unknown": "21m00Tcm4TlvDq8ikWAM"    # Default to male voice
        }
        
        voice_id = voice_mapping.get(speaker_gender.lower(), voice_mapping["unknown"])
        
        # Get API key from environment
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise Exception("ELEVENLABS_API_KEY not found in environment variables")
        
        # Create output directory
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Clean the script text
        cleaned_script = clean_script_for_tts(script_text)
        
        data = {
            "text": cleaned_script,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.75,  # Higher stability for more consistent voice
                "similarity_boost": 0.75,  # Higher similarity for better voice matching
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        print(f"Generating {speaker_gender} voiceover with ElevenLabs voice {voice_id}...")
        
        # Make API request
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
        
        # Generate unique filename
        import time
        timestamp = int(time.time())
        output_path = output_dir / f"voiceover_{speaker_gender}_{timestamp}.wav"
        
        # Save audio to file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"ElevenLabs voiceover generated successfully: {output_path}")
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"Failed to generate ElevenLabs voiceover: {str(e)}")


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
