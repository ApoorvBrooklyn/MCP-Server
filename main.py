"""
AI-Powered Viral Moment Content Pipeline
Main MCP Server using elevenlabs-mcp framework
"""

import os
import asyncio
from dotenv import load_dotenv
from elevenlabs_mcp import ElevenLabsMCPServer
from elevenlabs_mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

# Initialize the MCP server
server = ElevenLabsMCPServer("viral-moment-pipeline")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools for the viral moment content pipeline
    """
    return [
        Tool(
            name="download_youtube_audio",
            description="Download audio from a YouTube video URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube video URL to download audio from"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="transcribe_audio",
            description="Transcribe audio file to text using local Whisper model",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Path to the audio file to transcribe"
                    }
                },
                "required": ["audio_path"]
            }
        ),
        Tool(
            name="find_viral_moments",
            description="Analyze transcript to find the most viral-worthy moments",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript": {
                        "type": "string",
                        "description": "Full transcript text to analyze"
                    }
                },
                "required": ["transcript"]
            }
        ),
        Tool(
            name="generate_short_script",
            description="Generate a dynamic-length video script from viral moments (covers all viral moments)",
            inputSchema={
                "type": "object",
                "properties": {
                    "moment_summary": {
                        "type": "string",
                        "description": "Summary of viral moments to create script from (can be single or multiple)"
                    }
                },
                "required": ["moment_summary"]
            }
        ),
        Tool(
            name="generate_comprehensive_script",
            description="Generate a comprehensive script from multiple viral moments with full details",
            inputSchema={
                "type": "object",
                "properties": {
                    "viral_moments": {
                        "type": "array",
                        "description": "Array of viral moment objects with all details",
                        "items": {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string"},
                                "quote": {"type": "string"},
                                "viral_factor": {"type": "string"},
                                "priority": {"type": "string"},
                                "hook": {"type": "string"},
                                "timestamp": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["viral_moments"]
            }
        ),
        Tool(
            name="create_voiceover",
            description="Generate voiceover audio from script text using local TTS",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_text": {
                        "type": "string",
                        "description": "Script text to convert to voiceover"
                    },
                    "speaker_gender": {
                        "type": "string",
                        "description": "Speaker gender (male/female/unknown) for voice selection"
                    }
                },
                "required": ["script_text"]
            }
        ),
        Tool(
            name="create_voiceover_with_elevenlabs",
            description="Generate high-quality voiceover using ElevenLabs TTS with gender-appropriate voice",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_text": {
                        "type": "string",
                        "description": "Script text to convert to voiceover"
                    },
                    "speaker_gender": {
                        "type": "string",
                        "description": "Speaker gender (male/female/unknown) for voice selection"
                    }
                },
                "required": ["script_text"]
            }
        ),
        Tool(
            name="create_voiceover_with_auto_gender",
            description="Generate voiceover with automatic gender detection from transcript",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_text": {
                        "type": "string",
                        "description": "Script text to convert to voiceover"
                    },
                    "transcript": {
                        "type": "string",
                        "description": "Original transcript for gender detection"
                    },
                    "use_elevenlabs": {
                        "type": "boolean",
                        "description": "Whether to use ElevenLabs (true) or local TTS (false)"
                    }
                },
                "required": ["script_text", "transcript"]
            }
        ),
        Tool(
            name="create_engaging_video",
            description="Create an engaging video with multiple visual scenes, animations, and effects",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Script text for the video"
                    },
                    "title": {
                        "type": "string",
                        "description": "Video title"
                    },
                    "quote": {
                        "type": "string",
                        "description": "Key quote to highlight (optional)"
                    },
                    "voice_id": {
                        "type": "string",
                        "description": "ElevenLabs voice ID (optional)"
                    },
                    "speaker_gender": {
                        "type": "string",
                        "description": "Speaker gender (male/female/unknown) for voice selection"
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="create_video_with_auto_voice",
            description="Create an engaging video with automatic gender detection and appropriate voice selection",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Script text for the video"
                    },
                    "transcript": {
                        "type": "string",
                        "description": "Original transcript for gender detection"
                    },
                    "title": {
                        "type": "string",
                        "description": "Video title"
                    },
                    "quote": {
                        "type": "string",
                        "description": "Key quote to highlight (optional)"
                    }
                },
                "required": ["script", "transcript"]
            }
        ),
        Tool(
            name="create_person_narration_video",
            description="Create a video with a person narrating the script (better than text-only videos)",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Script text for the video"
                    },
                    "transcript": {
                        "type": "string",
                        "description": "Original transcript for gender detection"
                    },
                    "title": {
                        "type": "string",
                        "description": "Video title"
                    }
                },
                "required": ["script", "transcript"]
            }
        ),
        Tool(
            name="create_script_based_video",
            description="Create a high-quality video directly from script with professional narration",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Script text for the video"
                    },
                    "title": {
                        "type": "string",
                        "description": "Video title"
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="create_wav2lip_video",
            description="Create a professional video using Wav2Lip with natural, listenable audio",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "Script text for the video"
                    },
                    "title": {
                        "type": "string",
                        "description": "Video title"
                    },
                    "avatar_image_path": {
                        "type": "string",
                        "description": "Path to real human avatar image (optional, falls back to animated avatar if not provided)"
                    }
                },
                "required": ["script"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls for the viral moment content pipeline
    """
    try:
        if name == "download_youtube_audio":
            from tools.youtube_tool import get_audio_from_youtube
            url = arguments["url"]
            audio_path = get_audio_from_youtube(url)
            return [TextContent(type="text", text=f"Audio downloaded successfully: {audio_path}")]
        
        elif name == "transcribe_audio":
            from tools.transcription_tool import transcribe_audio
            audio_path = arguments["audio_path"]
            transcript = transcribe_audio(audio_path)
            return [TextContent(type="text", text=f"Transcript: {transcript}")]
        
        elif name == "find_viral_moments":
            from tools.llm_tool import find_key_moments
            transcript = arguments["transcript"]
            moments = find_key_moments(transcript)
            return [TextContent(type="text", text=f"Viral moments found: {moments}")]
        
        elif name == "generate_short_script":
            from tools.llm_tool import generate_short_script
            moment_summary = arguments["moment_summary"]
            script = generate_short_script(moment_summary)
            return [TextContent(type="text", text=f"Generated script: {script}")]
        
        elif name == "generate_comprehensive_script":
            from tools.llm_tool import generate_comprehensive_script
            viral_moments = arguments["viral_moments"]
            script = generate_comprehensive_script(viral_moments)
            return [TextContent(type="text", text=f"Generated comprehensive script: {script}")]
        
        elif name == "create_voiceover":
            from tools.voice_tool import create_voiceover
            script_text = arguments["script_text"]
            speaker_gender = arguments.get("speaker_gender", "unknown")
            voiceover_path = create_voiceover(script_text, speaker_gender=speaker_gender)
            return [TextContent(type="text", text=f"Voiceover created with {speaker_gender} voice: {voiceover_path}")]
        
        elif name == "create_voiceover_with_elevenlabs":
            from tools.voice_tool import create_voiceover_with_elevenlabs
            script_text = arguments["script_text"]
            speaker_gender = arguments.get("speaker_gender", "unknown")
            voiceover_path = create_voiceover_with_elevenlabs(script_text, speaker_gender=speaker_gender)
            return [TextContent(type="text", text=f"High-quality voiceover created with {speaker_gender} voice: {voiceover_path}")]
        
        elif name == "create_voiceover_with_auto_gender":
            from tools.voice_tool import create_voiceover, create_voiceover_with_elevenlabs
            from tools.llm_tool import detect_speaker_gender
            script_text = arguments["script_text"]
            transcript = arguments["transcript"]
            use_elevenlabs = arguments.get("use_elevenlabs", True)
            
            # Detect speaker gender from transcript
            print("🔍 Detecting speaker gender for voiceover...")
            speaker_gender = detect_speaker_gender(transcript)
            print(f"🎤 Detected speaker gender: {speaker_gender}")
            
            # Create voiceover with appropriate voice
            if use_elevenlabs:
                voiceover_path = create_voiceover_with_elevenlabs(script_text, speaker_gender=speaker_gender)
            else:
                voiceover_path = create_voiceover(script_text, speaker_gender=speaker_gender)
            
            return [TextContent(type="text", text=f"Voiceover created with auto-detected {speaker_gender} voice: {voiceover_path}")]
        
        elif name == "create_engaging_video":
            from tools.elevenlabs_video_tool import create_elevenlabs_video
            script = arguments["script"]
            title = arguments.get("title", "Viral Moment")
            quote = arguments.get("quote", "")
            voice_id = arguments.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
            speaker_gender = arguments.get("speaker_gender", "unknown")
            video_path = create_elevenlabs_video(script, voice_id, quote=quote, title=title, speaker_gender=speaker_gender)
            return [TextContent(type="text", text=f"Engaging video created: {video_path}")]
        
        elif name == "create_video_with_auto_voice":
            from tools.elevenlabs_video_tool import create_elevenlabs_video
            from tools.llm_tool import detect_speaker_gender
            script = arguments["script"]
            transcript = arguments["transcript"]
            title = arguments.get("title", "Viral Moment")
            quote = arguments.get("quote", "")
            
            # Detect speaker gender from transcript
            print("🔍 Detecting speaker gender...")
            speaker_gender = detect_speaker_gender(transcript)
            print(f"🎤 Detected speaker gender: {speaker_gender}")
            
            # Create video with appropriate voice
            video_path = create_elevenlabs_video(script, quote=quote, title=title, speaker_gender=speaker_gender)
            return [TextContent(type="text", text=f"Video created with {speaker_gender} voice: {video_path}")]
        
        elif name == "create_person_narration_video":
            from tools.elevenlabs_video_tool import create_person_narration_video
            from tools.llm_tool import detect_speaker_gender
            script = arguments["script"]
            transcript = arguments["transcript"]
            title = arguments.get("title", "Viral Moment")
            
            # Detect speaker gender from transcript
            print("🔍 Detecting speaker gender for person narration...")
            speaker_gender = detect_speaker_gender(transcript)
            print(f"🎤 Detected speaker gender: {speaker_gender}")
            
            # Create person narration video with appropriate voice
            video_path = create_person_narration_video(script, speaker_gender=speaker_gender, title=title)
            return [TextContent(type="text", text=f"Person narration video created with {speaker_gender} voice: {video_path}")]
        
        elif name == "create_script_based_video":
            from tools.elevenlabs_video_tool import create_script_based_video
            script = arguments["script"]
            title = arguments.get("title", "Viral Moment")
            
            # Create high-quality video directly from script
            video_path = create_script_based_video(script, title=title)
            return [TextContent(type="text", text=f"High-quality script-based video created: {video_path}")]
        
        elif name == "create_wav2lip_video":
            from tools.wav2lip_video_tool import create_wav2lip_video_with_audio
            script = arguments["script"]
            title = arguments.get("title", "Viral Moment")
            avatar_image_path = arguments.get("avatar_image_path")
            
            # Create Wav2Lip video with natural audio and optional real avatar
            video_path = create_wav2lip_video_with_audio(script, title=title, avatar_image_path=avatar_image_path)
            return [TextContent(type="text", text=f"Wav2Lip video with natural audio created: {video_path}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

async def main():
    """
    Main function to run the MCP server
    """
    print("Starting AI-Powered Viral Moment Content Pipeline Server...")
    print("Available tools:")
    print("- download_youtube_audio: Download audio from YouTube videos")
    print("- transcribe_audio: Transcribe audio using local Whisper")
    print("- find_viral_moments: Find ALL viral moments using Gemini AI (no limit)")
    print("- generate_short_script: Generate dynamic-length scripts covering all viral moments")
    print("- generate_comprehensive_script: Generate comprehensive scripts from detailed viral moments")
    print("- create_voiceover: Generate voiceovers using local TTS with gender support")
    print("- create_voiceover_with_elevenlabs: Generate high-quality voiceovers using ElevenLabs TTS")
    print("- create_voiceover_with_auto_gender: Generate voiceover with automatic gender detection")
    print("- create_engaging_video: Create engaging videos with multiple scenes, animations, and effects")
    print("- create_video_with_auto_voice: Create video with automatic gender detection and appropriate voice")
    
    # Run the server
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
