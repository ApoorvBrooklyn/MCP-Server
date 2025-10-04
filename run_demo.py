#!/usr/bin/env python3
"""
Demo launcher for the AI-Powered Viral Moment Content Pipeline
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import streamlit
        import yt_dlp
        import whisper
        import google.generativeai
        import TTS
        import requests
        from dotenv import load_dotenv
        from PIL import Image
        import librosa
        print("✅ All requirements are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main function to launch the demo"""
    print("🚀 AI-Powered Viral Moment Content Pipeline - Demo Launcher")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found. Please run from the project directory.")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check for .env file and API keys
    if not Path(".env").exists():
        print("⚠️  .env file not found. Creating template...")
        with open(".env", "w") as f:
            f.write("""# Google Gemini API Key (free tier)
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# ElevenLabs API Key for high-quality voice generation
# Get your API key from: https://elevenlabs.io/
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# HeyGen API Key for professional video generation
# Get your API key from: https://heygen.com/
HEYGEN_API_KEY=your_heygen_api_key_here

# Optional: Whisper model size (base, small, medium, large)
# base is fastest, large is most accurate
WHISPER_MODEL=base
""")
        print("📝 Please edit .env with your API keys")
    else:
        # Check if API keys are configured
        from dotenv import load_dotenv
        load_dotenv()
        
        google_key = os.getenv('GOOGLE_API_KEY')
        figma_key = os.getenv('FIGMA_API_KEY')
        figma_file_id = os.getenv('FIGMA_FILE_ID')
        
        if google_key and figma_key and figma_file_id:
            print("✅ API keys found in .env file - ready to go!")
        else:
            missing = []
            if not google_key: missing.append("GOOGLE_API_KEY")
            if not figma_key: missing.append("FIGMA_API_KEY")
            if not figma_file_id: missing.append("FIGMA_FILE_ID")
            print(f"⚠️  Missing API keys in .env: {', '.join(missing)}")
            print("💡 You can configure them in the demo sidebar or edit .env file")
    
    # Create necessary directories
    directories = ["downloads", "generated_audio", "generated_graphics"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("🎉 Starting Streamlit demo...")
    print("📡 The demo will open in your browser at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the demo")
    print("=" * 60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error launching demo: {e}")

if __name__ == "__main__":
    main()
