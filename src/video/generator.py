import os
import asyncio
import tempfile
from pathlib import Path
import logging
from typing import List, Dict, Any

from google.adk import Agent, LlmAgent, SequentialAgent
from google.adk.tool import FunctionTool
from google.adk.tool.google import WebSearchTool

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips

from src.api.youtube import upload_to_youtube
from src.utils.script import get_enhanced_script
from src.utils.images import search_images_online

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_script(title: str, description: str) -> str:
    logger.info(f"Generating script for: {title}")
    return await get_enhanced_script(title, description)

script_tool = FunctionTool(
    name="generate_script",
    description="Generate a narration script for a YouTube Short based on the title and description",
    function=generate_script
)

async def text_to_speech(script: str, output_path: str) -> str:
    logger.info("Converting script to speech")
    tts = gTTS(text=script, lang='en', slow=False)
    tts.save(output_path)
    return output_path

tts_tool = FunctionTool(
    name="text_to_speech",
    description="Convert text to speech and save as an audio file",
    function=text_to_speech
)

async def search_images(query: str, num_images: int = 5) -> List[str]:
    logger.info(f"Searching for images with query: {query}")
    return await search_images_online(query, num_images)

image_search_tool = FunctionTool(
    name="search_images",
    description="Search for relevant images based on the query",
    function=search_images
)

async def create_text_image(text: str, output_path: str) -> str:
    logger.info(f"Creating text image with: {text}")
    
    width, height = 1080, 1920
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        font = ImageFont.load_default()
    
    text_width = draw.textlength(text, font=font)
    text_x = (width - text_width) / 2
    text_y = height / 2
    
    draw.text((text_x, text_y), text, fill="white", font=font)
    
    image.save(output_path)
    
    return output_path

text_image_tool = FunctionTool(
    name="create_text_image",
    description="Create an image with the provided text",
    function=create_text_image
)

async def create_video(image_paths: List[str], audio_path: str, output_path: str) -> str:
    logger.info(f"Creating video from {len(image_paths)} images and audio")
    
    valid_images = []
    
    for img_path in image_paths:
        if os.path.exists(img_path):
            valid_images.append(img_path)
    
    if not valid_images:
        logger.warning("No valid images provided, creating placeholders")
        temp_dir = tempfile.mkdtemp()
        
        for i, text in enumerate(["This is a", "YouTube Short", "Created with", "Google ADK", "& Telegram"]):
            img_path = os.path.join(temp_dir, f"text_img_{i}.png")
            await create_text_image(text, img_path)
            valid_images.append(img_path)
    
    fps = 0.5
    
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        min_duration = len(valid_images) * 3
        if audio_duration > min_duration:
            fps = len(valid_images) / audio_duration
        
    clip = ImageSequenceClip(valid_images, fps=fps)
    
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        clip = clip.set_audio(audio)
        if audio.duration > clip.duration:
            clip = clip.loop(duration=audio.duration)
    
    clip.write_videofile(output_path, codec="libx264")
    
    return output_path

video_tool = FunctionTool(
    name="create_video",
    description="Create a video from a list of images and an audio file",
    function=create_video
)

async def generate_youtube_short(title: str, description: str) -> str:
    logger.info(f"Starting to generate YouTube Short for: {title}")
    
    workspace_dir = tempfile.mkdtemp()
    audio_path = os.path.join(workspace_dir, "narration.mp3")
    video_path = os.path.join(workspace_dir, "youtube_short.mp4")
    
    async def video_generation_workflow(agent_input: Dict[str, Any]) -> Dict[str, Any]:
        title = agent_input.get("title", "")
        description = agent_input.get("description", "")
        
        script_result = await agent.tools.generate_script(title=title, description=description)
        script = script_result.value
        
        audio_result = await agent.tools.text_to_speech(script=script, output_path=audio_path)
        
        image_results = await agent.tools.search_images(query=title, num_images=5)
        
        video_result = await agent.tools.create_video(
            image_paths=image_results.value,
            audio_path=audio_result.value,
            output_path=video_path
        )
        
        youtube_url = await upload_to_youtube(
            video_path=video_result.value,
            title=title,
            description=f"{description}\n\nGenerated using ADK and Telegram Bot"
        )
        
        return {"video_url": youtube_url}
    
    agent = SequentialAgent(
        workflow=video_generation_workflow,
        tools=[
            script_tool,
            tts_tool,
            image_search_tool,
            text_image_tool,
            video_tool,
            WebSearchTool()
        ]
    )
    
    result = await agent.run({"title": title, "description": description})
    
    return result.get("video_url", "https://youtube.com/shorts/placeholder") 