import os
import logging
import requests
import tempfile
from typing import List, Optional
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def search_images_online(query: str, num_images: int = 5, api_key: Optional[str] = None) -> List[str]:
    logger.info(f"Searching for images with query: {query}")
    
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    
    temp_dir = tempfile.mkdtemp()
    image_paths = []
    
    try:
        encoded_query = quote(query)
        url = f"https://api.unsplash.com/photos/random?query={encoded_query}&count={num_images}"
        
        unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        
        if unsplash_key:
            headers = {"Authorization": f"Client-ID {unsplash_key}"}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                images = response.json()
                
                for i, img in enumerate(images):
                    img_url = img["urls"]["regular"]
                    img_path = os.path.join(temp_dir, f"image_{i}.jpg")
                    
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        with open(img_path, "wb") as f:
                            f.write(img_response.content)
                        image_paths.append(img_path)
            else:
                logger.warning(f"Failed to fetch images from Unsplash: {response.status_code}")
        else:
            logger.warning("No Unsplash API key found, using placeholder images")
    
    except Exception as e:
        logger.error(f"Error searching for images: {e}")
    
    if not image_paths:
        from PIL import Image, ImageDraw, ImageFont
        
        for i in range(num_images):
            img_path = os.path.join(temp_dir, f"placeholder_{i}.jpg")
            
            img = Image.new('RGB', (1080, 1080), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
            
            text = f"{query} - Image {i+1}"
            text_width = draw.textlength(text, font=font)
            text_x = (1080 - text_width) / 2
            text_y = 1080 / 2
            
            draw.text((text_x, text_y), text, fill="white", font=font)
            
            img.save(img_path)
            image_paths.append(img_path)
    
    return image_paths 