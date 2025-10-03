# 🚀 Quick Start Guide

Get your AI-Powered Viral Moment Content Pipeline running in 5 minutes!

## ⚡ Quick Setup

1. **Install dependencies**:
   ```bash
   ./install.sh
   ```

2. **Get your API keys**:
   - **Google Gemini**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) → Create API key
   - **Figma**: Visit [Figma Developers](https://www.figma.com/developers/api#access-tokens) → Generate token

3. **Configure your .env file**:
   ```bash
   nano .env
   ```
   Update with your real API keys:
   ```
   GOOGLE_API_KEY=your_actual_google_api_key
   FIGMA_API_KEY=your_actual_figma_token
   FIGMA_FILE_ID=your_figma_file_id
   ```

4. **Test the pipeline**:
   ```bash
   python3 test_pipeline.py
   ```

5. **Start the MCP server**:
   ```bash
   python3 main.py
   ```

## 🎯 What You Get

Your MCP server exposes 6 powerful tools:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `download_youtube_audio` | Download audio from YouTube | YouTube URL | Audio file path |
| `transcribe_audio` | Convert audio to text | Audio file path | Transcript text |
| `find_viral_moments` | Find viral-worthy moments | Transcript | List of viral moments |
| `generate_short_script` | Create 60-second scripts | Moment summary | Video script |
| `create_voiceover` | Generate voiceover audio | Script text | Audio file path |
| `create_quote_graphic` | Create quote graphics | Quote text | Image file path |

## 🔄 Complete Workflow Example

```python
# 1. Download YouTube audio
audio_path = download_youtube_audio("https://youtube.com/watch?v=...")

# 2. Transcribe the audio
transcript = transcribe_audio(audio_path)

# 3. Find viral moments
moments = find_viral_moments(transcript)

# 4. Generate a script from the best moment
script = generate_short_script(moments[0]['summary'])

# 5. Create voiceover
voiceover = create_voiceover(script)

# 6. Create quote graphic
graphic = create_quote_graphic(moments[0]['quote'])
```

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" errors**:
```bash
pip3 install -r requirements.txt
```

**"FFmpeg not found"**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

**"API key invalid"**:
- Check your .env file has real API keys (not placeholders)
- Verify API keys are active and have proper permissions

**"Figma file not found"**:
- Make sure your Figma file is accessible
- Check the file ID is correct
- Ensure your API token has access to the file

### Getting Help

1. Check the full [README.md](README.md) for detailed documentation
2. Run `python3 test_pipeline.py` to diagnose issues
3. Check the console output for specific error messages

## 🎉 You're Ready!

Your AI-Powered Viral Moment Content Pipeline is now ready to transform long-form YouTube videos into viral short-form content automatically!

The entire pipeline runs locally (except for the free Gemini API calls) and costs nothing to operate. Perfect for content creators, marketers, and anyone looking to maximize their video content's reach.
