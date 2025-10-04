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
            description="Generate a 60-second video script from a viral moment",
            inputSchema={
                "type": "object",
                "properties": {
                    "moment_summary": {
                        "type": "string",
                        "description": "Summary of the viral moment to create script from"
                    }
                },
                "required": ["moment_summary"]
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
                    }
                },
                "required": ["script_text"]
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
        
        elif name == "create_voiceover":
            from tools.voice_tool import create_voiceover
            script_text = arguments["script_text"]
            voiceover_path = create_voiceover(script_text)
            return [TextContent(type="text", text=f"Voiceover created: {voiceover_path}")]
        
        
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
    print("- find_viral_moments: Find viral moments using Gemini AI")
    print("- generate_short_script: Generate 60-second scripts")
    print("- create_voiceover: Generate voiceovers using local TTS")
    
    # Run the server
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
