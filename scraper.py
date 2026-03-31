import re
import requests
from bs4 import BeautifulSoup
from utils import logger, retry

# Fetch raw HTML


def fetch_page(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = retry(lambda: requests.get(url, headers=headers, timeout=10))
    if response and response.status_code == 200:
        logger.info(f"Page fetched successfully: {url}")
        return response.text
    logger.error(f"Failed to fetch page: {url}")
    return None

# Parse song titles from HTML


def parse_song_titles(html, css_selector):
    """
    css_selector: the CSS selector targeting song title elements.
    Example: "span.song-title" or "td.tracklist-name"
    This varies per website — inspect the target page first.
    """
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(css_selector)

    titles = []
    for el in elements:
        title = el.get_text(strip=True)
        if title:
            titles.append(title)

    logger.info(f"Extracted {len(titles)} song titles")
    return titles

# Clean titles


def clean_titles(titles):
    junk_keywords = [
        "songwriter", "producer", "writer", "label",
        "album", "released", "genre", "featuring", "credits"
    ]

    cleaned = []
    for t in titles:
        t = re.sub(r"^\d+[\.\)]\s*", "", t)
        t = re.sub(r"\(feat\..*?\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\[.*?\]", "", t)
        t = t.strip()

        if not t:
            continue
        if len(t) < 2:
            continue
        if any(junk.lower() in t.lower() for junk in junk_keywords):
            logger.info(f"Skipping non-song entry: {t}")
            continue

        cleaned.append(t)

    cleaned = list(dict.fromkeys(cleaned))
    logger.info(f"{len(cleaned)} titles after cleaning")
    return cleaned

# Main scraper entry point


def scrape_playlist(url, css_selector):
    html = fetch_page(url)
    if not html:
        return []
    raw_titles = parse_song_titles(html, css_selector)
    return clean_titles(raw_titles)
