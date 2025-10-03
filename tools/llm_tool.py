"""
LLM Tool - Analyze content and generate scripts using Google Gemini API
"""

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
model = genai.GenerativeModel('gemini-pro')


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
        Analyze this video transcript and identify the 3 most viral-worthy moments that would work well for short-form content (TikTok, Instagram Reels, YouTube Shorts).

        For each moment, provide:
        1. A brief summary (1-2 sentences)
        2. The approximate timestamp (if available from context)
        3. Why it's viral-worthy (humor, shock value, educational, emotional, etc.)
        4. The exact quote or key phrase
        5. Suggested hook for the short video

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


def generate_short_script(moment_summary: str) -> str:
    """
    Generate a 60-second video script from a viral moment using Gemini AI
    
    Args:
        moment_summary (str): Summary of the viral moment to create script from
        
    Returns:
        str: 60-second video script
        
    Raises:
        Exception: If script generation fails
    """
    try:
        prompt = f"""
        Create a compelling 60-second video script based on this viral moment. The script should be optimized for short-form social media platforms (TikTok, Instagram Reels, YouTube Shorts).

        Requirements:
        - Hook the viewer in the first 3 seconds
        - Keep it under 60 seconds when spoken
        - Include clear visual cues in brackets [like this]
        - Make it engaging and shareable
        - End with a strong call-to-action

        Viral moment: {moment_summary}

        Format the script with timestamps and visual cues:
        [0-3s] Hook: [Visual cue] "Opening line that grabs attention"
        [3-15s] Setup: [Visual cue] "Context and background"
        [15-45s] Main content: [Visual cue] "The viral moment content"
        [45-60s] Call to action: [Visual cue] "Ending with engagement"

        Return only the script, no additional commentary.
        """

        response = model.generate_content(prompt)
        script = response.text.strip()
        
        print(f"Generated script (length: {len(script)} characters)")
        return script
        
    except Exception as e:
        raise Exception(f"Failed to generate script: {str(e)}")


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
