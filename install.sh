#!/bin/bash

# AI-Powered Viral Moment Content Pipeline - Installation Script

echo "🚀 Installing AI-Powered Viral Moment Content Pipeline"
echo "======================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. This is required for audio processing."
    echo "   Please install FFmpeg:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
else
    echo "✅ FFmpeg found: $(ffmpeg -version | head -n1)"
fi

# Create necessary directories
echo "📁 Creating output directories..."
mkdir -p downloads
mkdir -p generated_audio
mkdir -p generated_graphics

echo "✅ Output directories created"

# Check .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env .env.example
    echo "   Please edit .env with your API keys"
else
    echo "✅ .env file found"
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - GOOGLE_API_KEY (get from https://makersuite.google.com/app/apikey)"
echo "   - FIGMA_API_KEY (get from https://www.figma.com/developers/api#access-tokens)"
echo "   - FIGMA_FILE_ID (your Figma file ID)"
echo ""
echo "2. Run the test script:"
echo "   python3 test_pipeline.py"
echo ""
echo "3. Start the MCP server:"
echo "   python3 main.py"
echo ""
echo "🔗 For more information, see README.md"
