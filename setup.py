import os
import shutil
import subprocess
import sys
from pathlib import Path

def setup():
    """Set up the YouTube Shorts Generator Telegram Bot."""
    print("Setting up YouTube Shorts Generator Telegram Bot...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        sys.exit(1)
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create config file if it doesn't exist
    if not os.path.exists("config.env"):
        shutil.copy("config.env.example", "config.env")
        print("Created config.env file. Please edit it with your API keys and tokens.")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Edit the config.env file with your API keys and tokens")
    print("2. Run the bot with: python telegram_bot.py")

if __name__ == "__main__":
    setup() 