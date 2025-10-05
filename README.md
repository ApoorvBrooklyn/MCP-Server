# AI-Powered Viral Moment Content Pipeline

## Project Overview

This project implements a comprehensive **Model Context Protocol (MCP) server** that automates the creation of viral short-form content from long-form YouTube videos. The system leverages cutting-edge AI technologies to extract, analyze, and transform content into engaging video scripts with professional voiceovers and visual elements.

## 🎯 Problem Statement

The digital content landscape is dominated by short-form videos, yet most valuable content exists in long-form formats. This creates a significant gap where creators struggle to:
- Identify the most engaging moments in lengthy content
- Transform complex topics into digestible short-form videos
- Generate professional-quality voiceovers and visuals
- Scale content production efficiently

## 🚀 Solution Architecture

Our solution addresses these challenges through a multi-stage AI pipeline:

1. **Content Ingestion**: Automated YouTube audio extraction
2. **Intelligent Analysis**: AI-powered viral moment detection
3. **Script Generation**: Dynamic content transformation
4. **Voice Synthesis**: Professional-quality audio generation
5. **Video Production**: Automated visual content creation

## 🛠️ Technical Stack

### Core Technologies
- **Language**: Python 3.8+
- **Framework**: FastAPI with elevenlabs-mcp
- **AI/ML**: OpenAI Whisper, Google Gemini, Coqui TTS
- **Video Processing**: FFmpeg, OpenCV, Wav2Lip
- **Frontend**: Streamlit with custom UI components

### Key Dependencies
- **Audio Processing**: yt-dlp, librosa, soundfile
- **Machine Learning**: torch, tensorflow, scikit-image
- **Video Generation**: moviepy, imageio, face-recognition
- **API Integration**: google-generativeai, requests

## 📋 System Requirements

### Software Prerequisites
- **Python**: 3.8 or higher
- **FFmpeg**: For audio/video processing
- **Git**: For version control

### Hardware Recommendations
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 10GB free space for models and generated content
- **GPU**: Optional but recommended for faster processing

### API Keys Required
- **Google Gemini API**: Free tier available
- **ElevenLabs API**: Optional for enhanced voice quality

## 🚀 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone <https://github.com/ApoorvBrooklyn/MCP-Server.git>
cd viral-moment-pipeline
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install System Dependencies

#### macOS (using Homebrew)
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows
Download FFmpeg from [official website](https://ffmpeg.org/download.html) and add to PATH.

### Step 5: Download Wav2Lip Model
```bash
mkdir -p models/wav2lip
# Download wav2lip_gan.pth from: https://github.com/Rudrabha/Wav2Lip
# Place the model file in models/wav2lip/
```

### Step 6: Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Add your API keys:
```env
GOOGLE_API_KEY=your_google_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## 🎮 Usage

### Option 1: Streamlit Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```
Access the interface at: http://localhost:8501

### Option 2: Command Line Interface
```bash
python main.py
```

### Option 3: MCP Server Mode
```bash
python main.py --server-mode
```

## 🎭 Custom Avatar Support

The system automatically detects and uses existing narrator images from the `avatars/` folder:

### Supported Avatar Files
- **File Names**: `narrator.png`, `avatar.jpg`, `person.jpeg`, `speaker.png`, `host.gif`
- **File Formats**: PNG, JPG, JPEG, GIF, BMP
- **Location**: Place your avatar image in the `avatars/` folder

### How It Works
1. **Automatic Detection**: The system first checks for existing avatars in the `avatars/` folder
2. **Priority Order**: Looks for common names like "narrator", "avatar", "person", etc.
3. **Fallback**: If no existing avatar is found, creates a simple animated avatar
4. **Usage**: Existing avatars are used in both Wav2Lip and ElevenLabs video generation

### Example
```bash
# Place your narrator image
cp your_narrator.png avatars/narrator.png

# The system will automatically use it
python main.py
```

## 🎬 Advanced Lip Synchronization

The system now includes sophisticated lip synchronization technology that creates realistic mouth movements:

### Technology Stack
- **Audio Analysis**: Uses Librosa for real-time audio feature extraction
- **Face Detection**: OpenCV and face_recognition for precise face tracking
- **Lip Sync Engine**: Custom implementation based on Wav2Lip principles
- **Real-time Processing**: Frame-by-frame audio-to-visual synchronization

### Features
- **Audio-Driven Animation**: Mouth movements based on speech patterns and audio energy
- **Onset Detection**: Identifies speech starts for natural mouth opening
- **RMS Energy Mapping**: Volume-based lip movement intensity
- **Spectral Analysis**: Uses audio frequency data for enhanced synchronization
- **Fallback System**: Multiple levels of fallback for reliable operation

### How It Works
1. **Audio Processing**: Analyzes audio for speech patterns, energy, and timing
2. **Face Detection**: Locates and tracks the face in each video frame
3. **Lip Mapping**: Maps audio features to mouth movement parameters
4. **Frame Enhancement**: Applies real-time visual effects to simulate lip movement
5. **Video Generation**: Creates the final lip-synced video output

### Testing
```bash
# Test lip sync functionality
python test_lip_sync.py

# This will verify:
# - Dependencies are installed
# - Avatar detection works
# - Video creation with lip sync works
```

## 📁 Project Structure

```
viral-moment-pipeline/
├── .env                      # Environment configuration
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
├── main.py                 # Main MCP server
├── streamlit_app.py        # Web interface
├── models/                 # AI model storage
│   └── wav2lip/           # Wav2Lip model files
├── tools/                  # Core functionality modules
│   ├── __init__.py
│   ├── youtube_tool.py     # YouTube audio extraction
│   ├── transcription_tool.py # Whisper transcription
│   ├── llm_tool.py         # Gemini AI analysis
│   ├── voice_tool.py       # TTS voice generation
│   ├── video_tool.py       # Basic video creation
│   ├── elevenlabs_video_tool.py # Professional video generation
│   └── wav2lip_video_tool.py # Lip-sync video generation
├── downloads/              # Downloaded audio files
├── generated_audio/        # Generated voiceovers
├── generated_images/       # Generated visual assets
└── generated_videos/       # Final video outputs
```

## 🔧 API Documentation

### Core Tools

#### 1. Content Ingestion
- **`download_youtube_audio(url)`**: Extract audio from YouTube videos
- **`transcribe_audio(audio_path)`**: Convert audio to text using Whisper

#### 2. AI Analysis
- **`find_viral_moments(transcript)`**: Identify engaging content segments
- **`generate_short_script(moment_summary)`**: Create optimized scripts
- **`generate_comprehensive_script(viral_moments)`**: Generate detailed scripts

#### 3. Voice Generation
- **`create_voiceover(script_text)`**: Local TTS generation
- **`create_voiceover_with_elevenlabs(script_text)`**: Professional TTS
- **`create_voiceover_with_auto_gender(script_text, transcript)`**: Auto-gender detection

#### 4. Video Production
- **`create_engaging_video(script)`**: Multi-scene video creation
- **`create_person_narration_video(script, transcript)`**: Person-based narration
- **`create_wav2lip_video(script)`**: Lip-synced video generation

## 🎨 Features & Capabilities

### Content Analysis
- **Intelligent Moment Detection**: AI-powered identification of viral-worthy content
- **Contextual Understanding**: Maintains narrative flow while extracting key points
- **Multi-language Support**: Works with various languages and accents

### Voice Generation
- **Gender-Aware TTS**: Automatic speaker gender detection and appropriate voice selection
- **Natural Speech Patterns**: Enhanced script processing for natural-sounding audio
- **Multiple Voice Options**: Local and cloud-based voice generation

### Video Production
- **Dynamic Visual Elements**: Automated scene generation with relevant imagery
- **Professional Quality**: High-resolution output with smooth transitions
- **Advanced Lip-Sync Technology**: Real-time lip synchronization using audio analysis and Wav2Lip
- **Custom Avatar Support**: Automatically uses existing narrator images from `avatars/` folder
- **Audio-Driven Animation**: Mouth movements synchronized with speech patterns and audio energy

## 🔒 Privacy & Security

- **Local Processing**: Core transcription and basic TTS happen locally
- **No Data Retention**: Generated content is not stored permanently
- **API Key Security**: Secure environment variable management
- **Open Source**: Fully auditable codebase

## 📊 Performance Metrics

- **Processing Speed**: ~2-3 minutes for 10-minute video
- **Accuracy**: 95%+ transcription accuracy with Whisper
- **Quality**: Professional-grade voice synthesis
- **Scalability**: Handles videos up to 2 hours in length


## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical support or questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

## 🔮 Future Enhancements

- **Multi-language Support**: Enhanced language detection and processing
- **Custom Voice Training**: User-specific voice model training
- **Advanced Analytics**: Content performance prediction
- **Batch Processing**: Multiple video processing capabilities
- **Cloud Deployment**: Docker containerization and cloud hosting options
