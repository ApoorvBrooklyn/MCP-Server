import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')


def find_key_moments(transcript: str) -> List[Dict[str, Any]]:
    """
    Analyze transcript to find the most viral-worthy moments using Gemini AI
    
    Args:
        transcript (str): Full transcript text to analyze
        
    Returns:
        List[Dict]: List of viral moments with timestamps and summaries
        
    Raises:
        Exception: If analysis fails or API key is invalid
    """
    try:
        prompt = f"""
        Analyze this video transcript and identify ALL viral-worthy moments that would work well for short-form content (TikTok, Instagram Reels, YouTube Shorts). Don't limit yourself to a specific number - find as many genuinely viral moments as exist in the content.

        For each moment, provide:
        1. A brief summary (1-2 sentences)
        2. The approximate timestamp (if available from context)
        3. Why it's viral-worthy (humor, shock value, educational, emotional, etc.)
        4. The exact quote or key phrase
        5. Suggested hook for the short video
        6. Priority level (high/medium/low) for script inclusion

        Transcript:
        {transcript}

        Return your response as a JSON array with this structure:
        [
            {{
                "summary": "Brief description of the moment",
                "timestamp": "Approximate time (e.g., '2:30-3:15')",
                "viral_factor": "Why this moment is viral-worthy",
                "quote": "Exact quote or key phrase",
                "hook": "Suggested opening hook for short video",
                "priority": "high/medium/low",
                "confidence": 0.9
            }}
        ]
        """

        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Try to find JSON in the response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        # Parse JSON
        moments = json.loads(json_text)
        
        if not isinstance(moments, list):
            raise Exception("Invalid response format from Gemini")
        
        print(f"Found {len(moments)} viral moments")
        return moments
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {e}")
    except Exception as e:
        raise Exception(f"Failed to analyze transcript: {str(e)}")


def validate_and_improve_script(script: str) -> str:
    """
    Validate and improve script quality
    
    Args:
        script (str): Generated script text
        
    Returns:
        str: Improved script text
    """
    try:
        # Basic validation
        if not script or len(script.strip()) < 50:
            raise Exception("Script too short or empty")
        
        # Remove common issues
        script = script.strip()
        
        # Remove any markdown formatting
        script = script.replace("**", "").replace("*", "").replace("_", "")
        
        # Remove role labels and stage directions like VOICEOVER:, SFX:, [sound], (music), etc.
        lines = []
        for raw_line in script.splitlines():
            line = raw_line.strip()
            # Drop bracketed or parenthetical stage directions
            if (line.startswith("[") and line.endswith("]")) or (line.startswith("(") and line.endswith(")")):
                continue
            # Drop obvious role labels like VOICEOVER:, REPORTER:, SFX:, etc.
            if ":" in line:
                label, rest = line.split(":", 1)
                if label.strip().upper() in {"VOICEOVER", "REPORTER", "HOST", "NARRATOR", "SFX", "FX", "MUSIC", "ROCKY", "DONKEY", "SHREK"}:
                    line = rest.strip()
            # Remove any remaining inline bracketed/parenthetical annotations
            import re as _re
            line = _re.sub(r"\[[^\]]*\]", "", line)
            line = _re.sub(r"\([^)]*\)", "", line)
            line = line.strip()
            if line:
                lines.append(line)
        script = " ".join(lines)
        
        # Remove any "Script:" or "Here's the script:" prefixes
        if script.lower().startswith(("script:", "here's the script:", "script text:")):
            script = script.split(":", 1)[1].strip()
        
        # Ensure it starts with a hook
        if not any(script.lower().startswith(hook) for hook in ["you won't believe", "this is crazy", "wait until you hear", "can you believe", "here's what happened"]):
            # Add a hook if missing
            script = f"You won't believe what happened here. {script}"
        
        # Ensure proper ending
        if not any(script.lower().endswith(ending) for ending in ["!", "?", "...", "share this", "tell me what you think"]):
            script += " Share this if you found it interesting!"
        
        # Fix common grammar issues
        script = script.replace("  ", " ")  # Remove double spaces
        script = script.replace("..", ".")  # Fix double periods
        
        # Ensure proper capitalization
        sentences = script.split(". ")
        sentences = [sentence.strip().capitalize() for sentence in sentences if sentence.strip()]
        script = ". ".join(sentences)
        
        return script
        
    except Exception as e:
        print(f"⚠️ Script validation failed: {e}")
        return script


def detect_speaker_gender(transcript: str) -> str:
    """
    Detect the gender of the speaker from transcript content using Gemini AI
    
    Args:
        transcript (str): The transcript text to analyze
        
    Returns:
        str: "male", "female", or "unknown"
    """
    try:
        prompt = f"""
        Analyze this transcript and determine the likely gender of the speaker based on:
        - Speaking patterns and language use
        - Self-references and pronouns
        - Content context clues
        - Any explicit gender indicators

        Transcript: {transcript[:1000]}...

        Respond with only one word: "male", "female", or "unknown"
        """
        
        response = model.generate_content(prompt)
        gender = response.text.strip().lower()
        
        if gender in ["male", "female", "unknown"]:
            return gender
        else:
            return "unknown"
            
    except Exception as e:
        print(f"Warning: Could not detect speaker gender: {e}")
        return "unknown"


def generate_short_script(moment_summary: str, speaker_gender: str = "unknown") -> str:
    """
    Generate a dynamic-length audio script from viral moments using Gemini AI
    
    Args:
        moment_summary (str): Summary of viral moments to create script from (can be single or multiple)
        speaker_gender (str): Gender of the original speaker ("male", "female", "unknown")
        
    Returns:
        str: Dynamic-length audio script covering all viral moments
        
    Raises:
        Exception: If script generation fails
    """
    try:
        # Add gender context to the prompt
        gender_context = ""
        if speaker_gender == "male":
            gender_context = " The original speaker appears to be male, so write in a natural, engaging male voice style."
        elif speaker_gender == "female":
            gender_context = " The original speaker appears to be female, so write in a natural, engaging female voice style."
        
        prompt = f"""
        You are an expert content creator specializing in viral short-form videos. Create a compelling, engaging script that transforms the provided viral moments into a cohesive, shareable story.

        VIRAL MOMENTS TO WORK WITH:
        {moment_summary}

        SCRIPT REQUIREMENTS:
        1. HOOK (First 3 seconds): Start with the most shocking, surprising, or intriguing moment
        2. FLOW: Create smooth transitions between moments using connecting phrases like "But here's the thing...", "What's crazy is...", "And then...", "But wait..."
        3. TONE: Conversational, authentic, and engaging - like talking to a friend
        4. STRUCTURE: Hook → Build tension → Reveal/Climax → Strong ending
        5. EMOTION: Include emotional triggers (shock, surprise, humor, relatability)
        6. CLARITY: Make it easy to follow and understand
        7. IMPACT: Every sentence should add value or emotion

        WRITING STYLE (STRICT):
        - Single-person monologue only
        - NO labels like VOICEOVER:, REPORTER:, SFX:, MUSIC:
        - NO stage directions or sound cues (no brackets [] or parentheses ())
        - Use short, punchy sentences and natural speech patterns
        - Include specific details and numbers when available
        - End with a memorable statement

        QUALITY CHECK:
        - Does it grab attention immediately?
        - Is it easy to follow from start to finish?
        - Does it build emotional engagement?
        - Would someone want to share this?
        - Is it coherent and logical?

        {gender_context}

        Create a script that tells a complete, engaging story using ONLY the provided viral moments. Output only plain script text as a monologue with no labels or cues.
        """

        response = model.generate_content(prompt)
        script = response.text.strip()
        
        # Validate and improve script quality
        script = validate_and_improve_script(script)
        
        print(f"Generated script (length: {len(script)} characters)")
        return script
        
    except Exception as e:
        raise Exception(f"Failed to generate script: {str(e)}")


def generate_comprehensive_script(viral_moments: List[Dict[str, Any]], speaker_gender: str = "unknown") -> str:
    """
    Generate a comprehensive script from multiple viral moments using Gemini AI
    
    Args:
        viral_moments (List[Dict]): List of viral moments with all details
        speaker_gender (str): Gender of the original speaker ("male", "female", "unknown")
        
    Returns:
        str: Comprehensive audio script covering all viral moments
        
    Raises:
        Exception: If script generation fails
    """
    try:
        # Format viral moments for the prompt
        moments_text = ""
        for i, moment in enumerate(viral_moments, 1):
            moments_text += f"""
Moment {i}:
- Summary: {moment.get('summary', 'N/A')}
- Quote: {moment.get('quote', 'N/A')}
- Viral Factor: {moment.get('viral_factor', 'N/A')}
- Priority: {moment.get('priority', 'medium')}
- Hook: {moment.get('hook', 'N/A')}
- Timestamp: {moment.get('timestamp', 'N/A')}
"""
        
        # Add gender context to the prompt
        gender_context = ""
        if speaker_gender == "male":
            gender_context = " The original speaker appears to be male, so write in a natural, engaging male voice style."
        elif speaker_gender == "female":
            gender_context = " The original speaker appears to be female, so write in a natural, engaging female voice style."
        
        prompt = f"""
        Create a highly engaging, viral-worthy audio script that ONLY includes the viral moments provided below. This script should be optimized for short-form social media platforms (TikTok, Instagram Reels, YouTube Shorts) and designed to maximize engagement.

        CRITICAL REQUIREMENTS:
        - ONLY include the viral moments listed below - do not add any extra content, background information, or filler
        - Start with the most viral moment as a powerful hook (first 3 seconds are crucial for retention)
        - Create smooth, natural transitions between moments using connecting phrases
        - Keep it concise and impactful - every word should add value and emotion
        - Write in a conversational, authentic tone that feels natural and engaging
        - Use natural speech patterns with strategic pauses, emphasis, and rhythm
        - The script should be 30-90 seconds maximum
        - Focus on the most impactful quotes and key points from each moment
        - Add emotional triggers and storytelling elements to make it shareable
        - Use exclamations, questions, and dramatic pauses where appropriate
        - Make each moment flow into the next with smooth transitions
        - Include specific details and examples to make it relatable
        - End with a strong, memorable closing that encourages sharing

        VIRAL MOMENTS TO INCLUDE (ONLY THESE):
        {moments_text}

        Create a clean, engaging monologue that covers ONLY these viral moments in a compelling narrative flow. Focus on emotional impact, relatability, and shareability. No extra content, no filler, no background information.

        STRICT OUTPUT:
        - Single-person monologue only
        - No labels like VOICEOVER:, REPORTER:, SFX:, MUSIC:
        - No stage directions or sound cues (no [] or ())
        - Return only plain script text
        """

        response = model.generate_content(prompt)
        script = response.text.strip()
        
        # Validate and sanitize to enforce monologue without labels/SFX
        cleaned_script = validate_and_improve_script(script)
        print(f"Generated comprehensive script (length: {len(cleaned_script)} characters) covering {len(viral_moments)} viral moments")
        return cleaned_script
        
    except Exception as e:
        raise Exception(f"Failed to generate comprehensive script: {str(e)}")


def generate_quote_variations(quote: str) -> List[str]:
    """
    Generate multiple variations of a quote for different social media formats
    
    Args:
        quote (str): Original quote text
        
    Returns:
        List[str]: List of quote variations
    """
    try:
        prompt = f"""
        Create 5 different variations of this quote for social media posts. Each should be optimized for different platforms and character limits:

        Original quote: "{quote}"

        Create variations for:
        1. Twitter/X (280 characters max)
        2. Instagram caption (2,200 characters max)
        3. TikTok text overlay (short and punchy)
        4. LinkedIn post (professional tone)
        5. Facebook post (engaging and shareable)

        Return as a JSON array of strings.
        """

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        variations = json.loads(json_text)
        return variations
        
    except Exception as e:
        raise Exception(f"Failed to generate quote variations: {str(e)}")


def analyze_viral_potential(content: str) -> Dict[str, Any]:
    """
    Analyze the viral potential of content using various factors
    
    Args:
        content (str): Content to analyze
        
    Returns:
        Dict: Analysis results with scores and recommendations
    """
    try:
        prompt = f"""
        Analyze this content for viral potential and provide a detailed assessment:

        Content: {content}

        Evaluate on these factors (0-10 scale):
        1. Emotional impact (humor, shock, inspiration, etc.)
        2. Shareability (would people want to share this?)
        3. Relatability (can people connect with this?)
        4. Uniqueness (is this fresh and original?)
        5. Timing relevance (is this timely?)
        6. Visual appeal potential (would this work visually?)

        Also provide:
        - Overall viral score (0-100)
        - Target audience
        - Best platforms for this content
        - Suggested improvements
        - Hashtag recommendations

        Return as JSON with this structure:
        {{
            "scores": {{
                "emotional_impact": 8,
                "shareability": 7,
                "relatability": 9,
                "uniqueness": 6,
                "timing_relevance": 8,
                "visual_appeal": 7
            }},
            "overall_score": 75,
            "target_audience": "Young adults 18-35",
            "best_platforms": ["TikTok", "Instagram Reels"],
            "improvements": ["Add more visual elements", "Include trending music"],
            "hashtags": ["#viral", "#trending", "#fyp"]
        }}
        """

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        analysis = json.loads(json_text)
        return analysis
        
    except Exception as e:
        raise Exception(f"Failed to analyze viral potential: {str(e)}")


if __name__ == "__main__":
    # Test the functions
    test_transcript = "This is a test transcript about an amazing discovery that will change everything you know about technology. The breakthrough happened when scientists realized..."
    
    try:
        moments = find_key_moments(test_transcript)
        print(f"Test successful. Found {len(moments)} moments")
        
        if moments:
            script = generate_short_script(moments[0]['summary'])
            print(f"Generated script: {script[:100]}...")
    except Exception as e:
        print(f"Test failed: {e}")
