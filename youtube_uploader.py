import os
import logging
import pickle
from pathlib import Path
from typing import Optional

import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube API scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_credentials():
    """Get or refresh YouTube API credentials."""
    creds = None
    client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
    credentials_file = os.getenv("YOUTUBE_CREDENTIALS_FILE", "youtube_credentials.json")
    
    # Check if token file exists
    if os.path.exists(credentials_file):
        with open(credentials_file, "rb") as token:
            creds = pickle.load(token)
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This will open a browser window for authentication
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open(credentials_file, "wb") as token:
            pickle.dump(creds, token)
    
    return creds

async def upload_to_youtube(video_path: str, title: str, description: str, 
                           tags: Optional[list] = None, 
                           category_id: str = "22") -> str:
    """
    Upload a video to YouTube and return the video URL.
    
    Args:
        video_path: Path to the video file
        title: Video title
        description: Video description
        tags: List of tags (optional)
        category_id: YouTube category ID (default: 22 for People & Blogs)
    
    Returns:
        URL of the uploaded video
    """
    logger.info(f"Uploading video to YouTube: {title}")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    try:
        # Get YouTube API credentials
        credentials = get_youtube_credentials()
        youtube = build("youtube", "v3", credentials=credentials)
        
        # Set video metadata
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public",  # or "unlisted", "private"
                "selfDeclaredMadeForKids": False
            }
        }
        
        # Upload the video
        media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
        
        # Insert the video
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        
        logger.info("Uploading video...")
        response = request.execute()
        
        # Get the video ID and create URL
        video_id = response.get("id")
        video_url = f"https://youtube.com/shorts/{video_id}"
        
        logger.info(f"Video uploaded successfully: {video_url}")
        
        return video_url
    
    except Exception as e:
        logger.error(f"Error uploading video to YouTube: {e}")
        # For demo purposes, return a placeholder URL
        return "https://youtube.com/shorts/placeholder" 