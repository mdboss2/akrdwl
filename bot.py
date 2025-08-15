import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # Optional: to restrict usage

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send: /download <key> <save-name> <mpd-url>")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if ADMIN_ID and user_id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /download <key> <save-name> <mpd-url>")
        return

    key = context.args[0]
    save_name = context.args[1]
    mpd_url = context.args[2]

    await update.message.reply_text("Downloading... This may take a while.")

    cmd = [
        "N_m3u8DL-RE",
        "--key", key,
        "--save-name", save_name,
        mpd_url,
        "--mp4-real-time-decryption",
        "--live-real-time-merge",
        "--live-record-limit", "00:01:00",
        "--concurrent-download",
        "--mux-after-done", "mkv",
        "--del-after-done"
    ]

    try:
        subprocess.run(cmd, check=True)
        file_path = f"{save_name}.mkv"
        if os.path.exists(file_path):
            await update.message.reply_document(open(file_path, "rb"))
            os.remove(file_path)
        else:
            await update.message.reply_text("Download failed. File not found.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("download", download))
app.run_polling()
import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # Optional: to restrict usage

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send: /download <key> <save-name> <mpd-url>")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if ADMIN_ID and user_id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /download <key> <save-name> <mpd-url>")
        return

    key = context.args[0]
    save_name = context.args[1]
    mpd_url = context.args[2]

    await update.message.reply_text("Downloading... This may take a while.")

    cmd = [
        "N_m3u8DL-RE",
        "--key", key,
        "--save-name", save_name,
        mpd_url,
        "--mp4-real-time-decryption",
        "--live-real-time-merge",
        "--live-record-limit", "00:01:00",
        "--concurrent-download",
        "--mux-after-done", "mkv",
        "--del-after-done"
    ]

    try:
        subprocess.run(cmd, check=True)
        file_path = f"{save_name}.mkv"
        if os.path.exists(file_path):
            await update.message.reply_document(open(file_path, "rb"))
            os.remove(file_path)
        else:
            await update.message.reply_text("Download failed. File not found.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("download", download))
app.run_polling()
