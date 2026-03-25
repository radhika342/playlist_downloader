import os
import json
from googleapiclient.discovery import build
from dotenv import load_dotenv
from utils import logger, retry

load_dotenv()

CACHE_FILE = "cache.json"

# Load/save cache


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

# Build YouTube API client


def get_youtube_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not found in .env")
    return build("youtube", "v3", developerKey=api_key)

# Search for a song


def search_song(youtube, title):
    cache = load_cache()

    if title in cache:
        logger.info(f"Cache hit: {title}")
        return cache[title]

    def _search():
        response = youtube.search().list(
            q=title + " official audio",
            part="snippet",
            type="video",
            maxResults=1,
            videoCategoryId="10"
        ).execute()
        return response

    response = retry(_search)

    if not response or not response.get("items"):
        logger.warning(f"No results found for: {title}")
        return None

    video_id = response["items"][0]["id"]["videoId"]
    url = f"https://www.youtube.com/watch?v={video_id}"

    cache[title] = url
    save_cache(cache)

    logger.info(f"Found: {title} → {url}")
    return url

# Search all songs


def search_all_songs(titles):
    youtube = get_youtube_client()
    results = {}

    for title in titles:
        url = search_song(youtube, title)
        results[title] = url

    logger.info(
        f"YouTube search complete. {sum(1 for v in results.values() if v)} / {len(titles)} found")
    return results
