import os
import json
import googleapiclient.errors
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

# Search for a single song


def search_song(youtube, title):
    def _search():
        response = youtube.search().list(
            q=title + " official audio",
            part="snippet",
            type="video",
            maxResults=1,
            videoCategoryId="10"
        ).execute()
        return response

    try:
        response = retry(_search)
    except googleapiclient.errors.HttpError as e:
        if e.resp.status == 403:
            logger.error(
                "Quota exceeded — stopping all searches for today. Re-run tomorrow, cached songs will be skipped.")
            raise SystemExit(1)
        raise

    if not response or not response.get("items"):
        logger.warning(f"No results found for: {title}")
        return None

    video_id = response["items"][0]["id"]["videoId"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    return url

# Search all songs


def search_all_songs(titles):
    cache = load_cache()
    results = {}
    uncached = []

    # Split titles into cached and uncached
    for title in titles:
        if title in cache:
            logger.info(f"Cache hit: {title}")
            results[title] = cache[title]
        else:
            uncached.append(title)

    logger.info(f"{len(results)} from cache, {len(uncached)} need searching")

    # Only build client if there's anything to search
    if uncached:
        youtube = get_youtube_client()
        for title in uncached:
            url = search_song(youtube, title)
            results[title] = url
            if url:
                cache[title] = url
                save_cache(cache)

    logger.info(
        f"YouTube search complete. {sum(1 for v in results.values() if v)} / {len(titles)} found")
    return results
