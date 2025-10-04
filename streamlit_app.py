"""
AI-Powered Viral Moment Content Pipeline - Streamlit Frontend
Beautiful demo interface for the viral content creation pipeline
"""

import streamlit as st
import os
import tempfile
import json
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Check if API keys are already configured
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Page configuration
st.set_page_config(
    page_title="🚀 Viral Moment Pipeline",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .step-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 AI-Powered Viral Moment Content Pipeline</h1>', unsafe_allow_html=True)
st.markdown("Transform long-form YouTube videos into viral short-form content automatically!")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check if API keys are already loaded from .env
    keys_configured = GOOGLE_API_KEY
    
    if keys_configured:
        st.success("✅ API keys loaded from .env file")
        st.info("🔑 All API keys are configured and ready to use!")
    else:
        st.warning("⚠️ Some API keys are missing from .env file")
        
        # Only show input fields if keys are missing
        st.subheader("🔑 Missing API Keys")
        
        if not GOOGLE_API_KEY:
            google_key = st.text_input("Google API Key", type="password", help="Get from Google AI Studio")
            if google_key:
                os.environ['GOOGLE_API_KEY'] = google_key
                GOOGLE_API_KEY = google_key
        else:
            st.success("✅ Google API Key configured")
            
        st.info("🎬 Video generation is ready! Configure ElevenLabs API key for enhanced voice generation.")
    
    st.divider()
    
    # Settings
    st.subheader("🎛️ Settings")
    whisper_model = st.selectbox("Whisper Model", ["base", "small", "medium", "large"], 
                                index=["base", "small", "medium", "large"].index(os.getenv('WHISPER_MODEL', 'base')))
    os.environ['WHISPER_MODEL'] = whisper_model
    
    st.divider()
    
    # Status
    st.subheader("📊 Status")
    if GOOGLE_API_KEY:
        st.success("✅ All API keys configured")
        st.info("🚀 Ready to process videos!")
    else:
        missing_keys = []
        if not GOOGLE_API_KEY:
            missing_keys.append("Google API Key")
        
        st.error(f"❌ Missing: {', '.join(missing_keys)}")
        st.info("💡 Add missing keys to your .env file or use the sidebar")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🎬 Complete Pipeline", "🔧 Individual Tools", "📁 File Upload", "📊 Analytics"])

with tab1:
    st.header("🎬 Complete Viral Content Pipeline")
    st.markdown("Upload a YouTube URL and get viral content in 6 steps!")
    
    # YouTube URL input
    youtube_url = st.text_input("📺 YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("🚀 Generate Viral Content", type="primary", disabled=not GOOGLE_API_KEY):
        if not youtube_url:
            st.error("Please enter a YouTube URL")
        else:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Download YouTube audio
                status_text.text("📥 Step 1/6: Downloading YouTube audio...")
                progress_bar.progress(16)
                
                from tools.youtube_tool import get_audio_from_youtube
                audio_path = get_audio_from_youtube(youtube_url)
                
                st.success(f"✅ Audio downloaded: {os.path.basename(audio_path)}")
                
                # Step 2: Transcribe audio
                status_text.text("🎤 Step 2/6: Transcribing audio...")
                progress_bar.progress(33)
                
                from tools.transcription_tool import transcribe_audio
                transcript = transcribe_audio(audio_path)
                
                st.success(f"✅ Transcript completed ({len(transcript)} characters)")
                
                # Display transcript
                with st.expander("📝 View Full Transcript"):
                    st.text(transcript)
                
                # Step 3: Find viral moments
                status_text.text("🔍 Step 3/6: Finding viral moments...")
                progress_bar.progress(50)
                
                from tools.llm_tool import find_key_moments, detect_speaker_gender
                moments = find_key_moments(transcript)
                
                # Detect speaker gender
                speaker_gender = detect_speaker_gender(transcript)
                st.info(f"🎤 Detected speaker gender: {speaker_gender.title()}")
                
                st.success(f"✅ Found {len(moments)} viral moments")
                
                # Display viral moments
                for i, moment in enumerate(moments, 1):
                    with st.expander(f"🎯 Viral Moment {i}: {moment.get('summary', 'No summary')[:50]}..."):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Summary:** {moment.get('summary', 'N/A')}")
                            st.write(f"**Timestamp:** {moment.get('timestamp', 'N/A')}")
                            st.write(f"**Viral Factor:** {moment.get('viral_factor', 'N/A')}")
                        with col2:
                            st.write(f"**Quote:** {moment.get('quote', 'N/A')}")
                            st.write(f"**Hook:** {moment.get('hook', 'N/A')}")
                            st.write(f"**Confidence:** {moment.get('confidence', 'N/A')}")
                
                if moments:
                    # Step 4: Generate comprehensive script from all viral moments
                    status_text.text("📝 Step 4/6: Generating comprehensive script from all viral moments...")
                    progress_bar.progress(66)
                    
                    from tools.llm_tool import generate_comprehensive_script
                    script = generate_comprehensive_script(moments, speaker_gender)
                    
                    st.success("✅ Comprehensive script generated from all viral moments")
                    
                    # Display script
                    with st.expander("📄 View Generated Script"):
                        st.text(script)
                    
                    # Step 5: Create voiceover
                    status_text.text("🎵 Step 5/7: Creating voiceover...")
                    progress_bar.progress(71)
                    
                    from tools.voice_tool import create_voiceover
                    voiceover_path = create_voiceover(script, speaker_gender=speaker_gender)
                    
                    st.success(f"✅ Voiceover created: {os.path.basename(voiceover_path)}")
                    
                    # Play voiceover
                    st.audio(voiceover_path)
                    
                    # Step 6: Create person narration video
                    status_text.text("🎬 Step 6/7: Creating person narration video...")
                    progress_bar.progress(85)
                    
                    from tools.elevenlabs_video_tool import create_person_narration_video
                    video_path = create_person_narration_video(
                        script=script,
                        speaker_gender=speaker_gender,
                        title="Viral Moment"
                    )
                    
                    st.success(f"✅ Video created: {os.path.basename(video_path)}")
                    
                    # Display video
                    st.video(video_path)
                    
                    # Step 7: Pipeline complete
                    status_text.text("✅ Pipeline Complete!")
                    progress_bar.progress(100)
                    
                    st.success("🎉 All content generated successfully!")
                    
                    # Final results
                    status_text.text("🎉 Pipeline completed successfully!")
                    
                    # Download section
                    st.header("📥 Download Generated Content")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        with open(audio_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Audio",
                                data=file.read(),
                                file_name=os.path.basename(audio_path),
                                mime="audio/mpeg"
                            )
                    
                    with col2:
                        with open(voiceover_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Voiceover",
                                data=file.read(),
                                file_name=os.path.basename(voiceover_path),
                                mime="audio/wav"
                            )
                    
                    with col3:
                        with open(video_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Video",
                                data=file.read(),
                                file_name=os.path.basename(video_path),
                                mime="video/mp4"
                            )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                progress_bar.progress(0)
                status_text.text("Pipeline failed")

with tab2:
    st.header("🔧 Individual Tools")
    st.markdown("Test each tool individually")
    
    # YouTube Tool
    with st.expander("📺 YouTube Audio Download"):
        youtube_url_tool = st.text_input("YouTube URL", key="youtube_tool")
        if st.button("Download Audio", key="download_btn"):
            if youtube_url_tool:
                try:
                    from tools.youtube_tool import get_audio_from_youtube
                    audio_path = get_audio_from_youtube(youtube_url_tool)
                    st.success(f"Downloaded: {os.path.basename(audio_path)}")
                    st.audio(audio_path)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter a YouTube URL")
    
    # Transcription Tool
    with st.expander("🎤 Audio Transcription"):
        uploaded_audio = st.file_uploader("Upload Audio File", type=['mp3', 'wav', 'm4a'])
        if uploaded_audio and st.button("Transcribe Audio", key="transcribe_btn"):
            try:
                # Save uploaded file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_audio.read())
                    tmp_path = tmp_file.name
                
                from tools.transcription_tool import transcribe_audio
                transcript = transcribe_audio(tmp_path)
                st.success("Transcription completed!")
                st.text_area("Transcript", transcript, height=200)
                
                # Clean up
                os.unlink(tmp_path)
            except Exception as e:
                st.error(f"Error: {e}")
    
    # LLM Tools
    with st.expander("🤖 AI Analysis"):
        transcript_text = st.text_area("Enter transcript text", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Find Viral Moments", key="viral_btn"):
                if transcript_text and GOOGLE_API_KEY:
                    try:
                        from tools.llm_tool import find_key_moments
                        moments = find_key_moments(transcript_text)
                        st.success(f"Found {len(moments)} viral moments")
                        for i, moment in enumerate(moments, 1):
                            st.write(f"**{i}.** {moment.get('summary', 'No summary')}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter transcript text and configure Google API key")
        
        with col2:
            moment_summary = st.text_input("Moment Summary")
            if st.button("Generate Script", key="script_btn"):
                if moment_summary and GOOGLE_API_KEY:
                    try:
                        from tools.llm_tool import generate_short_script
                        script = generate_short_script(moment_summary)
                        st.success("Script generated!")
                        st.text_area("Generated Script", script, height=150)
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please enter moment summary and configure Google API key")
    
    # Voice Tool
    with st.expander("🎵 Voice Generation"):
        script_text = st.text_area("Script Text", height=100)
        if st.button("Generate Voiceover", key="voice_btn"):
            if script_text:
                try:
                    from tools.voice_tool import create_voiceover
                    voiceover_path = create_voiceover(script_text)
                    st.success("Voiceover generated!")
                    st.audio(voiceover_path)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter script text")
    
    # ElevenLabs Video Tool
    with st.expander("🎬 ElevenLabs Video Generation"):
        st.write("Create professional videos using ElevenLabs TTS and visual elements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_script = st.text_area("Video Script", height=100, key="elevenlabs_script")
            video_quote = st.text_input("Key Quote", key="elevenlabs_quote")
            video_title = st.text_input("Video Title", value="Viral Moment", key="elevenlabs_title")
        
        with col2:
            voice_id = st.selectbox("Voice", ["21m00Tcm4TlvDq8ikWAM", "AZnzlk1XvdvUeBnXmlld", "EXAVITQu4vr4xnSDxMaL"], key="elevenlabs_voice")
            bg_color = st.color_picker("Background Color", value="#000000", key="elevenlabs_bg")
            text_color = st.color_picker("Text Color", value="#FFFFFF", key="elevenlabs_text")
        
        if st.button("Create ElevenLabs Video", key="elevenlabs_btn"):
            if video_script:
                try:
                    from tools.elevenlabs_video_tool import create_elevenlabs_video
                    video_path = create_elevenlabs_video(
                        script=video_script,
                        voice_id=voice_id,
                        quote=video_quote,
                        title=video_title,
                        background_color=bg_color,
                        text_color=text_color
                    )
                    st.success("Video created with ElevenLabs!")
                    st.video(video_path)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Please enter script text")
    

with tab3:
    st.header("📁 File Management")
    
    # Show generated files
    st.subheader("📂 Generated Files")
    
    # Check for generated directories
    directories = ["downloads", "generated_audio", "generated_graphics"]
    
    for directory in directories:
        if os.path.exists(directory):
            files = os.listdir(directory)
            if files:
                st.write(f"**{directory.title()}:**")
                for file in files:
                    file_path = os.path.join(directory, file)
                    file_size = os.path.getsize(file_path)
                    st.write(f"  - {file} ({file_size:,} bytes)")
            else:
                st.write(f"**{directory.title()}:** (empty)")
        else:
            st.write(f"**{directory.title()}:** (not created yet)")
    
    # File cleanup
    if st.button("🗑️ Clean Generated Files"):
        for directory in directories:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    os.remove(os.path.join(directory, file))
        st.success("Files cleaned up!")

with tab4:
    st.header("📊 Analytics & Insights")
    
    # Pipeline statistics
    st.subheader("📈 Pipeline Statistics")
    
    # Count files in each directory
    stats = {}
    for directory in ["downloads", "generated_audio", "generated_graphics"]:
        if os.path.exists(directory):
            stats[directory] = len(os.listdir(directory))
        else:
            stats[directory] = 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Audio Files", stats.get("downloads", 0))
    with col2:
        st.metric("Voiceovers", stats.get("generated_audio", 0))
    with col3:
        st.metric("Graphics", stats.get("generated_graphics", 0))
    
    # Feature overview
    st.subheader("🎯 Features Overview")
    
    features = [
        "🎬 YouTube Audio Download",
        "🎤 Local Audio Transcription", 
        "🤖 AI Viral Moment Detection",
        "📝 60-Second Script Generation",
        "🎵 Local Voice Synthesis",
        "🎨 Quote Graphic Creation"
    ]
    
    for feature in features:
        st.write(feature)
    
    # API Status
    st.subheader("🔑 API Status")
    
    api_status = {
        "Google Gemini": "✅ Configured" if GOOGLE_API_KEY else "❌ Not configured",
    }
    
    for api, status in api_status.items():
        st.write(f"**{api}:** {status}")

# Footer
st.markdown("---")
st.markdown("🚀 **AI-Powered Viral Moment Content Pipeline** - Transform your content into viral moments!")
st.markdown("Built with ❤️ using Python, Streamlit, and free AI tools")
