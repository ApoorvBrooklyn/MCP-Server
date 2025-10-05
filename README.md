# Viral Moment Pipeline

Turn long YouTube videos into short, shareable clips. Now simplified: monologue-only scripts, ElevenLabs narration, and a looped background using the repository’s `Sample_Video.mp4`.

## What it does
- Detects viral moments from a YouTube transcript (Gemini)
- Generates a single-person monologue script (no VOICEOVER/SFX labels)
- Creates high‑quality narration (ElevenLabs)
- Loops `Sample_Video.mp4` to match narration length (FFmpeg) and muxes audio


## Requirements
- Python 3.11+
- FFmpeg in PATH (`ffmpeg`, `ffprobe`)
- API keys in `.env`:
  - `GOOGLE_API_KEY`
  - `ELEVENLABS_API_KEY`

Install deps:
```bash
pip install -r requirements.txt
```

FFmpeg (macOS):
```bash
brew install ffmpeg
```

## Quick start
Run the Streamlit app:
```bash
cd viral-moment-pipeline
streamlit run streamlit_app.py
```
Pipeline steps in the UI:
1) Download audio → 2) Transcribe → 3) Find moments → 4) Generate monologue → 5) ElevenLabs voiceover → 6) Loop `Sample_Video.mp4` and mux audio

Result videos/audio are saved under `generated_videos/` and `generated_audio/`.

## How it works (under the hood)
- Script generation: `tools/llm_tool.py` enforces monologue output and sanitizes any labels/cues
- Narration: `tools/voice_tool.py#create_high_quality_voiceover`
- Video: `tools/video_tool.py#create_looped_video_with_audio` uses FFmpeg to loop `Sample_Video.mp4` to the narration duration
- Streamlit pipeline updated to use the looped-video path by default

## Keeping media out of Git
`*.mp4` is ignored, but if `Sample_Video.mp4` was previously committed, untrack it:
```bash
git rm --cached viral-moment-pipeline/Sample_Video.mp4
git commit -m "Stop tracking Sample_Video.mp4; ignore media"
git push
```

## Troubleshooting
- Missing ElevenLabs key: set `ELEVENLABS_API_KEY` in `.env`
- FFmpeg not found: install and ensure `ffmpeg`/`ffprobe` are on PATH

## Project structure
```
viral-moment-pipeline/
├── main.py
├── streamlit_app.py
├── tools/
│   ├── llm_tool.py           # moments + monologue scripts
│   ├── voice_tool.py         # ElevenLabs voiceover
│   └── video_tool.py         # loop Sample_Video.mp4 + mux audio
├── Sample_Video.mp4          # background (kept local, ignored by Git)
├── generated_audio/
└── generated_videos/
```

