from scraper import scrape_playlist
from youtube_api import search_all_songs
from downloader import process_song
from utils import logger

# target playlist page
PLAYLIST_URL = "https://www.billboard.com/charts/hot-100/"

# inspect element on page
CSS_SELECTOR = "h3#title-of-a-story"


def main():
    logger.info("═" * 50)
    logger.info("Pipeline started")

    # Step 1: Scrape titles
    logger.info("Step 1: Scraping playlist...")
    titles = scrape_playlist(PLAYLIST_URL, CSS_SELECTOR)
    if not titles:
        logger.error(
            "No titles extracted. Check URL and CSS selector. Exiting.")
        return

    logger.info(f"Titles found: {titles}")

    # Step 2: Search YouTube
    logger.info("Step 2: Searching YouTube...")
    search_results = search_all_songs(titles)

    # Step 3: Download and convert
    logger.info("Step 3: Downloading and converting...")
    success, failed = 0, 0

    for title, url in search_results.items():
        if not url:
            logger.warning(f"Skipping (no URL): {title}")
            failed += 1
            continue

        logger.info(f"Processing: {title}")
        ok = process_song(title, url)
        if ok:
            success += 1
        else:
            failed += 1

    # Summary
    logger.info("═" * 50)
    logger.info(f"Pipeline complete. Success: {success} | Failed: {failed}")
    logger.info("═" * 50)


if __name__ == "__main__":
    main()
