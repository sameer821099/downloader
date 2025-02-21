import os
import time
import yt_dlp
import humanize
from pyrogram import Client, filters

# 🔧 Bot Configuration
API_ID = "23007772"  # Replace with your API ID
API_HASH = "d3adae78666d4faf40302e50494aab6b"  # Replace with your API Hash
BOT_TOKEN = "7548871019:AAHwFWLMgq8D2rwtYf6Y5CGYtwlILQiS1G0"  # Replace with your Bot Token

bot = Client("insta_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Function to check & install ffmpeg
def check_ffmpeg():
    if os.system("ffmpeg -version") != 0:
        print("❌ ERROR: ffmpeg is not installed! Installing now...")

        if os.name == "posix":  # Linux & Termux
            os.system("pkg install ffmpeg -y" if "com.termux" in os.getenv("HOME", "") else "sudo apt install ffmpeg -y")
        elif os.name == "nt":  # Windows
            os.system("choco install ffmpeg -y")

        print("✅ ffmpeg installed successfully! Please restart your bot.")
        
check_ffmpeg()  # Run the ffmpeg check

# ✅ Ensure yt-dlp is up to date
os.system("pip install --upgrade yt-dlp")

# 🎉 Start Command
@bot.on_message(filters.command("start"))
def start(_, message):
    message.reply_text(
        "👋 **Hello!**\n"
        "🚀 Send me an **Instagram video link**, and I'll **download** it for you!\n\n"
        "🎥 **Supports:** Video & Audio\n"
        "⏳ **Shows:** Download Time & File Size\n"
        "✅ **No Login Needed!**\n\n"
        "💡 *Just send an Instagram URL!*"
    )

# 🎬 Download Instagram Video
@bot.on_message(filters.text & filters.regex(r"instagram\.com"))
def download_instagram_video(_, message):
    url = message.text
    msg = message.reply_text("🔄 **Processing your request...**")

    options = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "merge_output_format": "mp4",  # Ensures proper merging
        "http_headers": {"User-Agent": "Mozilla/5.0"}  # Spoof User-Agent to bypass restrictions
    }

    start_time = time.time()  # ⏳ Start Timer

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            msg.edit_text("❌ **Download failed. Please try again.**")
            return

        elapsed_time = time.time() - start_time  # ⏳ Stop Timer
        file_size = os.path.getsize(filename)

        # 🚨 Check if file is too large for Telegram (Max 2GB)
        if file_size > 2 * 1024 * 1024 * 1024:
            msg.edit_text("❌ **File too large! Telegram only supports up to 2GB.**")
            os.remove(filename)  # 🗑️ Delete the file to save space
            return

        msg.edit_text(
            f"✅ **Download Complete!**\n"
            f"📁 **File:** {info.get('title', 'Unknown Video')}\n"
            f"📏 **Size:** {humanize.naturalsize(file_size)}\n"
            f"⏳ **Time Taken:** {round(elapsed_time, 2)}s"
        )

        message.reply_video(video=filename, caption="🎥 **Here is your video!** 🔥")

        os.remove(filename)  # 🗑️ Delete File After Sending

    except yt_dlp.utils.DownloadError as e:
        msg.edit_text(f"❌ **Download Error:** {str(e)}\n\n📌 Make sure the video is public and try again.")
    except Exception as e:
        msg.edit_text(f"❌ **Unexpected Error:** {str(e)}")

bot.run()