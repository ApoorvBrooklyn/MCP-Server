"""
Test script for the AI-Powered Viral Moment Content Pipeline
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_pipeline():
    """
    Test the complete pipeline with a sample YouTube video
    """
    print("🧪 Testing AI-Powered Viral Moment Content Pipeline")
    print("=" * 60)
    
    # Test URL (replace with actual YouTube video)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    
    try:
        # Step 1: Download YouTube audio
        print("\n📥 Step 1: Downloading YouTube audio...")
        from tools.youtube_tool import get_audio_from_youtube
        audio_path = get_audio_from_youtube(test_url)
        print(f"✅ Audio downloaded: {audio_path}")
        
        # Step 2: Transcribe audio
        print("\n🎤 Step 2: Transcribing audio...")
        from tools.transcription_tool import transcribe_audio
        transcript = transcribe_audio(audio_path)
        print(f"✅ Transcript length: {len(transcript)} characters")
        print(f"📝 First 200 chars: {transcript[:200]}...")
        
        # Step 3: Find viral moments
        print("\n🔍 Step 3: Finding viral moments...")
        from tools.llm_tool import find_key_moments
        moments = find_key_moments(transcript)
        print(f"✅ Found {len(moments)} viral moments")
        for i, moment in enumerate(moments, 1):
            print(f"   {i}. {moment.get('summary', 'No summary')}")
        
        # Step 4: Generate script
        if moments:
            print("\n📝 Step 4: Generating short script...")
            from tools.llm_tool import generate_short_script
            script = generate_short_script(moments[0]['summary'])
            print(f"✅ Script generated: {len(script)} characters")
            print(f"📄 Script preview: {script[:300]}...")
            
            # Step 5: Create voiceover
            print("\n🎵 Step 5: Creating voiceover...")
            from tools.voice_tool import create_voiceover
            voiceover_path = create_voiceover(script)
            print(f"✅ Voiceover created: {voiceover_path}")
            
            # Step 6: Create quote graphic
            print("\n🎨 Step 6: Creating quote graphic...")
            from tools.design_tool import create_quote_graphic
            quote = moments[0].get('quote', 'Test quote')
            graphic_path = create_quote_graphic(quote)
            print(f"✅ Quote graphic created: {graphic_path}")
        
        print("\n🎉 Pipeline test completed successfully!")
        print("\n📁 Generated files:")
        print(f"   - Audio: {audio_path}")
        if moments:
            print(f"   - Voiceover: {voiceover_path}")
            print(f"   - Graphic: {graphic_path}")
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check your .env file has valid API keys")
        print("   3. Ensure you have FFmpeg installed for audio processing")
        print("   4. Verify the YouTube URL is accessible")

def test_individual_tools():
    """
    Test individual tools without the full pipeline
    """
    print("\n🔧 Testing individual tools...")
    
    # Test LLM tool with sample text
    print("\n🤖 Testing LLM tool...")
    try:
        from tools.llm_tool import find_key_moments
        sample_transcript = "This is a test transcript about an amazing discovery that will change everything you know about technology. The breakthrough happened when scientists realized that the traditional approach was completely wrong."
        moments = find_key_moments(sample_transcript)
        print(f"✅ LLM tool working: Found {len(moments)} moments")
    except Exception as e:
        print(f"❌ LLM tool failed: {e}")
    
    # Test voice tool with sample text
    print("\n🎵 Testing voice tool...")
    try:
        from tools.voice_tool import create_voiceover
        sample_script = "Hello! This is a test of the voice generation system."
        voiceover_path = create_voiceover(sample_script)
        print(f"✅ Voice tool working: {voiceover_path}")
    except Exception as e:
        print(f"❌ Voice tool failed: {e}")
    
    # Test design tool with sample quote
    print("\n🎨 Testing design tool...")
    try:
        from tools.design_tool import create_quote_graphic
        sample_quote = "This is a test quote for the design tool!"
        graphic_path = create_quote_graphic(sample_quote)
        print(f"✅ Design tool working: {graphic_path}")
    except Exception as e:
        print(f"❌ Design tool failed: {e}")

if __name__ == "__main__":
    print("🚀 AI-Powered Viral Moment Content Pipeline - Test Suite")
    print("=" * 60)
    
    # Check environment setup
    print("\n🔍 Checking environment setup...")
    required_keys = ['GOOGLE_API_KEY', 'FIGMA_API_KEY', 'FIGMA_FILE_ID']
    missing_keys = [key for key in required_keys if not os.getenv(key) or os.getenv(key) == f'your_{key.lower()}_here']
    
    if missing_keys:
        print(f"⚠️  Missing or placeholder API keys: {', '.join(missing_keys)}")
        print("   Please update your .env file with real API keys")
        print("\n🔧 Running individual tool tests instead...")
        test_individual_tools()
    else:
        print("✅ All API keys configured")
        print("\n🚀 Running full pipeline test...")
        asyncio.run(test_pipeline())
