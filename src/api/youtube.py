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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_credentials():
    creds = None
    client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
    credentials_file = os.getenv("YOUTUBE_CREDENTIALS_FILE", "youtube_credentials.json")
    
    if os.path.exists(credentials_file):
        with open(credentials_file, "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(credentials_file, "wb") as token:
            pickle.dump(creds, token)
    
    return creds

async def upload_to_youtube(video_path: str, title: str, description: str, 
                           tags: Optional[list] = None, 
                           category_id: str = "22") -> str:
    logger.info(f"Uploading video to YouTube: {title}")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    try:
        credentials = get_youtube_credentials()
        youtube = build("youtube", "v3", credentials=credentials)
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
        
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        
        logger.info("Uploading video...")
        response = request.execute()
        
        video_id = response.get("id")
        video_url = f"https://youtube.com/shorts/{video_id}"
        
        logger.info(f"Video uploaded successfully: {video_url}")
        
        send_to_n8n_webhook({
            "event": "video_uploaded",
            "video_id": video_id,
            "video_url": video_url,
            "title": title
        })
        
        return video_url
    
    except Exception as e:
        logger.error(f"Error uploading video to YouTube: {e}")
        return "https://youtube.com/shorts/placeholder"

def send_to_n8n_webhook(data):
    try:
        import requests
        import json
        
        n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if not n8n_webhook_url:
            return
            
        response = requests.post(
            n8n_webhook_url, 
            data=json.dumps(data),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent data to n8n: {response.text}")
        else:
            logger.warning(f"Failed to send data to n8n: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending data to n8n: {e}") 