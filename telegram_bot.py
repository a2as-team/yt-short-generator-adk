import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Load environment variables
load_dotenv("config.env")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
TITLE, DESCRIPTION = range(2)

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
            return
        
        self.application = Application.builder().token(self.token).build()
        self._register_handlers()
    
    def _register_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("create", self.create_video_start)],
            states={
                TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_title)],
                DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_description)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        await update.message.reply_text(
            "Hi! I'm a YouTube Shorts generator bot. Use /create to start making a new video."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text(
            "Use /create to start the process of creating a YouTube Short.\n"
            "I'll guide you through providing a title and description."
        )

    async def create_video_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the video creation conversation."""
        await update.message.reply_text(
            "Let's create a YouTube Short! First, please send me the title for your video."
        )
        return TITLE

    async def get_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the title and ask for description."""
        context.user_data["title"] = update.message.text
        await update.message.reply_text(
            f"Great! Your video title is: \"{context.user_data['title']}\"\n"
            "Now, please provide a detailed description of what you want in the video."
        )
        return DESCRIPTION

    async def get_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the description and start the video generation process."""
        context.user_data["description"] = update.message.text
        
        await update.message.reply_text(
            f"Thanks! I've received your request:\n\n"
            f"Title: {context.user_data['title']}\n"
            f"Description: {context.user_data['description']}\n\n"
            "I'll now generate your YouTube Short. This may take some time. I'll notify you when it's ready."
        )
        
        await self.process_video_request(update, context)
        
        return ConversationHandler.END

    async def process_video_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process the video creation request using ADK."""
        try:
            from src.video.generator import generate_youtube_short
            
            title = context.user_data["title"]
            description = context.user_data["description"]
            
            await update.message.reply_text("Starting to generate your video...")
            
            video_url = await generate_youtube_short(title, description)
            
            await update.message.reply_text(
                f"Your YouTube Short has been created and uploaded! 🎉\n"
                f"You can view it here: {video_url}"
            )
            
            self._send_to_n8n_webhook(title, description, video_url)
            
        except Exception as e:
            logger.error(f"Error in video generation: {e}")
            await update.message.reply_text(
                "Sorry, there was an error generating your video. Please try again later."
            )

    def _send_to_n8n_webhook(self, title, description, video_url):
        try:
            import requests
            import json
            
            n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
            if not n8n_webhook_url:
                logger.info("N8N integration not configured, skipping webhook")
                return
                
            payload = {
                "title": title,
                "description": description,
                "video_url": video_url,
                "timestamp": str(datetime.datetime.now())
            }
            
            response = requests.post(
                n8n_webhook_url, 
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent data to n8n: {response.text}")
            else:
                logger.warning(f"Failed to send data to n8n: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending data to n8n: {e}")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        await update.message.reply_text("Video creation canceled.")
        return ConversationHandler.END
        
    def run(self):
        if not self.token:
            return
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import datetime
    bot = TelegramBot()
    bot.run() 