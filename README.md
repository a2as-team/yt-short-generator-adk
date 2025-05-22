# YouTube Shorts Generator Telegram Bot

A Telegram bot that uses Google's Agent Development Kit (ADK) to generate and upload YouTube Shorts based on a title and description.

## Features

- **Telegram Bot Interface**: Easy-to-use conversational interface to generate videos
- **Script Generation**: Uses ADK's LlmAgent (powered by Gemini) to create engaging scripts
- **Text-to-Speech**: Converts the script to natural-sounding speech
- **Video Generation**: Creates a video with synchronized images and audio
- **YouTube Upload**: Automatically uploads the generated video to YouTube as a Short
- **n8n Integration**: Webhook support for n8n automation workflows

## Setup

### Prerequisites

- Python 3.9+
- A Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Google API Key for Gemini (for LLM capabilities)
- YouTube API credentials for video uploads
- Unsplash API key (optional, for better images)
- n8n webhook URL (optional, for workflow automation)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/telegram-adk-bot.git
cd telegram-adk-bot
```

2. Install dependencies:
```bash
python setup.py
```

3. Edit the `config.env` file with your API keys and tokens.

4. For YouTube uploads, you'll need to:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com)
   - Enable the YouTube Data API v3
   - Create OAuth credentials (download as client_secret.json)

5. For n8n integration (optional):
   - Set up an n8n instance
   - Create a webhook node in your workflow
   - Add the webhook URL to your config.env file

## Usage

1. Start the bot:
```bash
python telegram_bot.py
```

2. Open Telegram and start a chat with your bot.

3. Use the `/create` command to start creating a YouTube Short.

4. Provide a title and description when prompted.

5. Wait for the bot to generate and upload your video.

## Project Structure

```
telegram-adk-bot/
├── config.env                  # Configuration environment variables
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── setup.py                    # Setup script
├── telegram_bot.py             # Main bot application
├── src/                        # Source code directory
│   ├── api/                    # API integration modules
│   │   ├── __init__.py
│   │   └── youtube.py          # YouTube API integration
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── images.py           # Image search and manipulation
│   │   └── script.py           # Script generation with Gemini
│   └── video/                  # Video processing modules
│       ├── __init__.py
│       └── generator.py        # Main video generation logic
```

## n8n Integration

The bot supports integration with n8n workflow automation. When configured, it sends webhooks on events like video creation and upload completion.

To set up n8n integration:

1. Add your n8n webhook URL to the `config.env` file:
```
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/path
```

2. Create a webhook node in n8n to receive the data.

3. Build your workflow to process the video data.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 