import os
import yt_dlp
import imageio_ffmpeg
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_LIMIT = 2 * 1024 * 1024 * 1024  # 2GB
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

WELCOME_TEXT = (
    "🎬 Send me an MPD/M3U8/HLS link.\n"
    "I'll download **best video + best audio** and merge into MP4.\n\n"
    "You can also send `/cookie` to upload a cookies.txt file for private streams."
)

# Store cookies.txt path
COOKIES_FILE = "cookies.txt"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 Please send me your `cookies.txt` file.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if doc.file_name.endswith(".txt"):
        file_path = await doc.get_file()
        await file_path.download_to_drive(COOKIES_FILE)
        await update.message.reply_text("✅ Cookies file saved successfully.")
    else:
        await update.message.reply_text("❌ Please send a valid `cookies.txt` file.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid MPD/M3U8 URL.")
        return

    await update.message.reply_text("⏳ Downloading best quality video + audio...")

    ydl_opts = {
        "outtmpl": "output.%(ext)s",
        "merge_output_format": "mp4",
        "format": "bv*+ba/best",
        "quiet": True,
        "noprogress": True,
        "ffmpeg_location": FFMPEG_PATH
    }

    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find downloaded file
        file_path = None
        for f in os.listdir():
            if f.startswith("output."):
                file_path = f
                break

        if not file_path:
            await update.message.reply_text("⚠️ File not found after download.")
            return

        file_size = os.path.getsize(file_path)
        if file_size > TELEGRAM_LIMIT:
            await update.message.reply_text("⚠️ File size exceeds Telegram 2GB limit.")
            os.remove(file_path)
            return

        await update.message.reply_video(video=InputFile(file_path), supports_streaming=True)
        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN not found in environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cookie", cookie))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    app.run_polling()

if __name__ == "__main__":
    main()
