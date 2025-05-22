import os
import logging
from typing import Dict, Any

from google.adk import LlmAgent
from google.adk.tool import FunctionTool
from google.adk.tool.google import WebSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScriptGenerator:
    """A class that generates scripts for YouTube Shorts using ADK's LlmAgent."""
    
    def __init__(self, api_key: str = None):
        """Initialize the ScriptGenerator with Google API key."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("No API key provided. Script generation may be limited.")
        
        # Create the LLM agent
        self.agent = LlmAgent(
            model="gemini-pro",
            tools=[WebSearchTool()],
            config={"api_key": self.api_key} if self.api_key else {}
        )
    
    async def generate_script(self, title: str, description: str, duration_seconds: int = 30) -> str:
        """
        Generate a script for a YouTube Short based on the title and description.
        
        Args:
            title: The title of the video
            description: The description of the video
            duration_seconds: Target duration in seconds (default: 30)
        
        Returns:
            A script that can be narrated in the specified duration
        """
        # Calculate approximate word count (average person speaks ~150 words per minute)
        target_word_count = int((duration_seconds / 60) * 150)
        
        prompt = f"""Generate a compelling script for a YouTube Short with the title: "{title}"
        
Based on this description: "{description}"

The script should:
1. Be approximately {target_word_count} words (to fit in {duration_seconds} seconds when spoken)
2. Have a strong hook in the first few seconds
3. Be engaging and interesting for the audience
4. Have a clear flow from beginning to end
5. End with a call to action
6. Use a conversational, direct tone appropriate for social media

Only return the script text with no additional formatting, notes, or explanations.
"""
        
        response = await self.agent.generate(prompt)
        script = response.text.strip()
        
        logger.info(f"Generated script ({len(script.split())} words)")
        return script

async def get_enhanced_script(title: str, description: str) -> str:
    """Generate an enhanced script using the ScriptGenerator."""
    generator = ScriptGenerator()
    return await generator.generate_script(title, description) 