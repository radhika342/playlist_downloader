import os
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
from utils import logger, retry, sanitize_filename, ensure_output_dir

OUTPUT_DIR = "output"
TEMP_DIR = "output/temp"

# Download video stream


def download_video(url, title):
    os.makedirs(TEMP_DIR, exist_ok=True)
    safe_name = sanitize_filename(title)
    output_path = os.path.join(TEMP_DIR, safe_name + ".mp4")

    if os.path.exists(output_path):
        logger.info(f"Already downloaded (video): {title}")
        return output_path

    def _download():
        yt = YouTube(url)
        stream = (
            yt.streams.filter(only_audio=True)
              .order_by("abr")
              .desc()
              .first()
        )
        if not stream:
            raise Exception(f"No audio stream found for: {title}")
        stream.download(output_path=TEMP_DIR, filename=safe_name + ".mp4")
        return output_path

    result = retry(_download)
    if result:
        logger.info(f"Downloaded: {title}")
    return result

# Convert video to MP3


def convert_to_audio(video_path, title):
    safe_name = sanitize_filename(title)
    audio_path = os.path.join(OUTPUT_DIR, safe_name + ".mp3")

    if os.path.exists(audio_path):
        logger.info(f"Already converted: {title}")
        return audio_path

    try:
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, logger=None)
        clip.close()
        logger.info(f"Converted to audio: {title}")
        return audio_path
    except Exception as e:
        logger.error(f"Conversion failed for {title}: {e}")
        return None

# Cleanup temp video file


def cleanup_temp(video_path):
    try:
        os.remove(video_path)
        logger.info(f"Cleaned up temp file: {video_path}")
    except Exception as e:
        logger.warning(f"Could not delete temp file: {e}")

# Full pipeline for one song


def process_song(title, url):
    ensure_output_dir(OUTPUT_DIR)
    video_path = download_video(url, title)
    if not video_path:
        return False

    audio_path = convert_to_audio(video_path, title)
    cleanup_temp(video_path)
    return audio_path is not None
