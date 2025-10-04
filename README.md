# AI-Powered Viral Moment Content Pipeline

A complete MCP (Model Context Protocol) server that automatically processes long-form YouTube videos to generate short-form viral content including scripts, voiceovers, and videos - all using free and open-source tools.

## 🚀 Features

- **YouTube Audio Download**: Extract audio from any YouTube video using `yt-dlp`
- **Local Transcription**: Transcribe audio using OpenAI's Whisper model locally
- **AI Analysis**: Find viral moments using Google's free Gemini API
- **Script Generation**: Create 60-second video scripts from viral moments
- **Local Voice Generation**: Generate voiceovers using Coqui TTS
- **Video Generation**: Create professional videos with ElevenLabs TTS and visual elements

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Framework**: FastAPI with elevenlabs-mcp
- **YouTube**: yt-dlp
- **Transcription**: openai-whisper (local)
- **LLM**: Google Gemini (free tier)
- **TTS**: Coqui TTS (local) + ElevenLabs (professional)
- **Video**: FFmpeg + Pillow for video generation

## 📋 Prerequisites

- Python 3.8 or higher
- Google API key (free tier)
- ElevenLabs API key (optional, for enhanced voice generation)
- FFmpeg (for audio and video processing)

## 🚀 Quick Start

### Option 1: Streamlit Demo (Recommended) 🎨
1. **Install dependencies**:
   ```bash
   ./install.sh
   ```

2. **Get your API keys**:
   - **Google Gemini**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) → Create API key
   - **ElevenLabs** (optional): Visit [ElevenLabs](https://elevenlabs.io) → Get API key for enhanced voice generation

3. **Configure your .env file**:
   ```bash
   nano .env
   ```
   Update with your real API keys:
   ```
   GOOGLE_API_KEY=your_actual_google_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ```

4. **Launch the beautiful demo**:
   ```bash
   python3 run_demo.py
   ```
   The demo will open at: http://localhost:8501

### Option 2: Command Line Interface 💻
1. **Test the pipeline**:
   ```bash
   python3 test_pipeline.py
   ```

2. **Start the MCP server**:
   ```bash
   python3 main.py
   ```

## 🔧 API Keys Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

### ElevenLabs API (Optional)
1. Visit [ElevenLabs](https://elevenlabs.io)
2. Sign up and get your API key
3. Add it to your `.env` file as `ELEVENLABS_API_KEY`
4. This enables professional-quality voice generation for videos

## 📁 Project Structure

```
viral-moment-pipeline/
├── .env                  # API keys and configuration
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── main.py              # Main MCP server
└── tools/               # Individual tool modules
    ├── __init__.py
    ├── youtube_tool.py      # YouTube audio download
    ├── transcription_tool.py # Local Whisper transcription
    ├── llm_tool.py          # Gemini AI analysis
    ├── voice_tool.py        # Coqui TTS voice generation
    └── elevenlabs_video_tool.py # ElevenLabs video generation
```

## 🎯 Usage

The server exposes 5 main tools that can be called by AI models:

1. **download_youtube_audio(url)**: Download audio from YouTube
2. **transcribe_audio(audio_path)**: Transcribe audio to text
3. **find_viral_moments(transcript)**: Find viral-worthy moments
4. **generate_short_script(moment_summary)**: Create 60-second scripts
5. **create_voiceover(script_text)**: Generate voiceover audio

## 🔒 Privacy & Cost

- **100% Local Processing**: Audio transcription and basic voice generation happen locally
- **Free APIs Only**: Uses only free tiers of Google Gemini (ElevenLabs is optional)
- **No Data Storage**: No user data is stored or transmitted to third parties
- **Open Source**: All code is open source and auditable

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
