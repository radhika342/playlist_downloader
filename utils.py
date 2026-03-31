import logging
import time
import os
import re

# Logging setup


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("pipeline.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logger()

# Retry with exponential backoff


def retry(func, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            # Don't retry quota errors
            if "quotaExceeded" in str(e):
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay * (2 ** attempt))
    logger.error(f"All {retries} attempts failed for {func.__name__}")
    return None

# Sanitize filename


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip().replace(" ", "_")
    return name[:100]

# Ensure output folder exists


def ensure_output_dir(path="output"):
    os.makedirs(path, exist_ok=True)
    logger.info(f"Output directory ready: {path}")
