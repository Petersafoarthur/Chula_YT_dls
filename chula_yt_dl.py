import logging
import os
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Bot token is missing! Please set TELEGRAM_BOT_TOKEN in your .env file.")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def extract_youtube_playlist_links(playlist_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if "entries" in info:
            return [entry["url"] for entry in info["entries"]]
    return []

async def start(update: Update, context):
    await update.message.reply_text("Babe❤️ send YouTube links, and I'll download them for you!")

async def download_youtube_videos(update: Update, context):
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Darling💕 Please send a valid YouTube link!")
        return

    if "playlist?" in url:
        video_links = extract_youtube_playlist_links(url)
        if not video_links:
            await update.message.reply_text("❌ Failed to retrieve YouTube playlist!")
            return
        await update.message.reply_text(f"Downloading {len(video_links)} videos from playlist, please wait... 😊")
    else:
        video_links = [url]
    
    output_path = "downloads/%(title)s.%(ext)s"
    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": output_path,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for video_url in video_links:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                await update.message.reply_video(video=open(filename, "rb"), caption="You're Welcome Baby 😊❤️ Here is your YouTube video!")
                os.remove(filename)  # Clean up after sending
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to download YouTube video: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_youtube_videos))
    
    app.run_polling()

if __name__ == "__main__":
    main()
