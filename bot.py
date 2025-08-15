import os
import yt_dlp
import imageio_ffmpeg
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Renderನಲ್ಲಿ Dashboard → Environment → Add Variable → BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_LIMIT = 2 * 1024 * 1024 * 1024  # ~2 GB
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

WELCOME = (
    "🎬 MPD/M3U8/HLS ಲಿಂಕ್ ಕಳುಹಿಸಿ — ನಾನು **best video + best audio** merge ಮಾಡಿ MP4 ಆಗಿ ಕಳುಹಿಸುತ್ತೇನೆ.\n"
    "🔒 Private streams? `/cookie` ಕಳುಹಿಸಿ cookies.txt upload ಮಾಡಿ (DRM ಇಲ್ಲದವು ಮಾತ್ರ)."
)

COOKIES_FILE = "cookies.txt"

def _human(n: int | None) -> str:
    if not n:
        return "unknown"
    units = ["B","KB","MB","GB","TB"]
    i = 0
    x = float(n)
    while x >= 1024 and i < len(units) - 1:
        x /= 1024.0
        i += 1
    return f"{x:.2f} {units[i]}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)

async def cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📂 ದಯವಿಟ್ಟು ನಿಮ್ಮ `cookies.txt` ಫೈಲ್ ಅನ್ನು ಡಾಕ್ಯುಮೆಂಟ್ ಆಗಿ ಕಳುಹಿಸಿ.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return
    name = (doc.file_name or "").lower()
    if not name.endswith(".txt"):
        await update.message.reply_text("❌ `cookies.txt` ಫೈಲ್ ಮಾತ್ರ ಸ್ವೀಕರಿಸಲಾಗುತ್ತದೆ.")
        return
    tgfile = await doc.get_file()
    await tgfile.download_to_drive(COOKIES_FILE)
    await update.message.reply_text("✅ Cookies file saved. ಮುಂದಕ್ಕೆ private (DRM ಇಲ್ಲದ) streams ಪ್ರಯತ್ನಿಸಿ.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = (update.message.text or "").strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ ಸರಿಯಾದ MPD/M3U8/HLS ಲಿಂಕ್ ಕಳುಹಿಸಿ.")
        return

    await update.message.reply_text("🔎 Analyzing stream (best video+audio ಆಯ್ಕೆ)…")

    base_opts = {
        "quiet": True,
        "noprogress": True,
        "nocheckcertificate": True,
        "ffmpeg_location": FFMPEG_PATH,
    }
    if os.path.exists(COOKIES_FILE):
        base_opts["cookiefile"] = COOKIES_FILE

    # Try to estimate size
    est_bytes = None
    title = "video"
    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title") or title
    except Exception as e:
        await update.message.reply_text(f"⚠️ Analyze error: {e}")
        return

    try:
        probe_opts = {
            **base_opts,
            "format": "bv*+ba/best",
            "merge_output_format": "mp4",
            "simulate": True,
            "forcejson": True,
            "dump_single_json": True,
        }
        with yt_dlp.YoutubeDL(probe_opts) as ydl:
            selected = ydl.extract_info(url, download=False)
            rfs = selected.get("requested_formats") or []
            if rfs:
                est_bytes = sum((f.get("filesize") or f.get("filesize_approx") or 0) for f in rfs)
            else:
                est_bytes = selected.get("filesize") or selected.get("filesize_approx")
    except Exception:
        pass

    if est_bytes and est_bytes >= TELEGRAM_LIMIT:
        await update.message.reply_text(
            f"⚠️ ಅಂದಾಜು size { _human(est_bytes) } → Telegram ಗರಿಷ್ಠ ~2GB. "
            "ಕಡಿಮೆ quality source/format ಪ್ರಯತ್ನಿಸಿ."
        )
        return

    await update.message.reply_text("⬇️ Download & merge ಆರಂಭವಾಗಿದೆ…")

    out_name_tmpl = "merged.%(ext)s"
    ydl_opts = {
        **base_opts,
        "outtmpl": out_name_tmpl,
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "retries": 3,
        "concurrent_fragment_downloads": 5,
        "fragment_retries": 10,
        "http_chunk_size": 10 * 1024 * 1024,  # 10MB
        "postprocessors": [
            {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}
        ],
    }

    downloaded_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Locate result
        for f in os.listdir("."):
            if f.startswith("merged.") and (f.endswith(".mp4") or f.endswith(".mkv") or f.endswith(".m4a")):
                downloaded_file = f
                break

        if not downloaded_file:
            await update.message.reply_text("⚠️ Download complete, but file not found.")
            return

        size = os.path.getsize(downloaded_file)
        if size >= TELEGRAM_LIMIT:
            await update.message.reply_text(
                f"⚠️ Final size { _human(size) } > Telegram limit. ಕಡಿಮೆ quality ಪ್ರಯತ್ನಿಸಿ."
            )
            os.remove(downloaded_file)
            return

        send_name = f"{title}.mp4" if downloaded_file.endswith((".mp4", ".mkv")) else f"{title}.m4a"
        if downloaded_file.endswith((".mp4", ".mkv")):
            await update.message.reply_video(
                video=InputFile(downloaded_file),
                filename=send_name,
                supports_streaming=True
            )
        else:
            await update.message.reply_audio(
                audio=InputFile(downloaded_file),
                filename=send_name
            )
        await update.message.reply_text("✅ Done!")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Download/Merge error: {e}")
    finally:
        try:
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
        except Exception:
            pass

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in environment.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cookie", cookie))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    # Long-polling keeps the worker active (Render free-tier won't idle this)
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
        
