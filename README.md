# YouTube Shorts Generator Telegram Bot

A Telegram bot that uses Google's Agent Development Kit (ADK) to generate and upload YouTube Shorts based on a title and description.

## Features

- **Telegram Bot Interface**: Easy-to-use conversational interface to generate videos
- **Script Generation**: Uses ADK's LlmAgent (powered by Gemini) to create engaging scripts
- **Text-to-Speech**: Converts the script to natural-sounding speech
- **Video Generation**: Creates a video with synchronized images and audio
- **YouTube Upload**: Automatically uploads the generated video to YouTube as a Short

## Setup

### Prerequisites

- Python 3.9+
- A Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Google API Key for Gemini (for LLM capabilities)
- YouTube API credentials for video uploads

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/telegram-adk-bot.git
cd telegram-adk-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a config file:
```bash
cp config.env.example config.env
```

4. Edit the `config.env` file with your API keys and tokens.

5. For YouTube uploads, you'll need to:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com)
   - Enable the YouTube Data API v3
   - Create OAuth credentials (download as client_secret.json)

## Usage

1. Start the bot:
```bash
python telegram_bot.py
```

2. Open Telegram and start a chat with your bot.

3. Use the `/create` command to start creating a YouTube Short.

4. Provide a title and description when prompted.

5. Wait for the bot to generate and upload your video.

## How It Works

1. The user provides a title and description through the Telegram bot
2. The ADK agent generates a script using LlmAgent (Gemini)
3. The script is converted to speech using gTTS
4. Relevant images are generated/selected for the video
5. A video is created combining the images and audio
6. The video is uploaded to YouTube as a Short
7. The YouTube URL is sent back to the user in Telegram

## Architecture

This project uses Google's Agent Development Kit (ADK) for orchestrating the video generation process:

- **SequentialAgent**: Coordinates the workflow steps
- **LlmAgent**: Generates the script content
- **FunctionTools**: Handles specific tasks like text-to-speech and video creation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 