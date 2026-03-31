import os
import yt_dlp
from utils import logger, retry, sanitize_filename, ensure_output_dir

OUTPUT_DIR = "output"

# Download and convert to MP3 directly via yt-dlp


def download_video(url, title):
    safe_name = sanitize_filename(title)
    audio_path = os.path.join(OUTPUT_DIR, safe_name + ".mp3")

    if os.path.exists(audio_path):
        logger.info(f"Already downloaded: {title}")
        return audio_path

    def _download():
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(OUTPUT_DIR, safe_name),
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return audio_path

    result = retry(_download)
    if result:
        logger.info(f"Downloaded and converted: {title}")
    return result

# Full pipeline for one song


def process_song(title, url):
    ensure_output_dir(OUTPUT_DIR)
    audio_path = download_video(url, title)
    return audio_path is not None
