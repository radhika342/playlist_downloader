# Automated Playlist-to-Audio Downloader

A Python pipeline that scrapes song titles from an online playlist, searches for them on YouTube using the YouTube Data API, and downloads them as MP3 files, fully automated, end to end.

---

## Features

- Scrapes song titles from any playlist webpage
- Searches YouTube Data API for each song
- Downloads audio and converts to MP3 via yt-dlp and FFmpeg
- Caches API results to avoid re-searching on re-runs
- Skips already-downloaded songs
- Retry logic with exponential backoff on failures
- Structured logging to terminal and `pipeline.log`
- Graceful quota handling — stops cleanly when API limit is hit

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core language |
| requests | Fetching playlist pages |
| BeautifulSoup (bs4) | Parsing HTML |
| YouTube Data API v3 | Searching songs on YouTube |
| yt-dlp | Downloading audio from YouTube |
| FFmpeg | Converting audio to MP3 |
| moviepy | (replaced by yt-dlp postprocessor) |
| os / shutil | File management |
| logging | Pipeline logging |
| python-dotenv | Secure API key management |

---

## Project Structure

```
playlist-audio-downloader/
├── scraper.py          # Fetches and parses song titles from playlist page
├── youtube_api.py      # Searches YouTube for each song, caches results
├── downloader.py       # Downloads and converts audio to MP3
├── utils.py            # Logging, retry logic, filename helpers
├── main.py             # Orchestrates the full pipeline
├── output/             # Final MP3 files saved here
├── cache.json          # Auto-generated, stores API search results
├── pipeline.log        # Auto-generated, full run logs
├── .env                # Your API key (never commit this)
├── .gitignore
└── requirements.txt
```

---

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- A YouTube Data API v3 key

### Install FFmpeg

```bash
# Mac
brew install ffmpeg

# Windows
winget install ffmpeg
```

### Get a YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Go to Credentials -> Create API Key
5. Copy the key

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/radhika342/playlist_downloader.git
cd playlist_downloader
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create a `.env` file in the project root:
```
YOUTUBE_API_KEY=your_api_key_here
```

---

## Configuration

Open `main.py` and set these two values before running:

```python
PLAYLIST_URL = "https://example.com/your-playlist"   # URL of the playlist page
CSS_SELECTOR = "span.song-title"                      # CSS selector for song title elements
```

### Finding the CSS selector

1. Open your playlist page in a browser
2. Right-click a song title → **Inspect**
3. Find the HTML element wrapping the title text
4. Note its tag and class, e.g. `<span class="track-name">` → selector is `span.track-name`

---

## Running the Pipeline

```bash
python main.py
```

### What happens step by step

1. **Scrape** — fetches the playlist page and extracts song titles
2. **Search** — queries YouTube API for each title, caches results to `cache.json`
3. **Download** — downloads best audio stream for each song via yt-dlp
4. **Convert** — converts to MP3 at 192kbps using FFmpeg
5. **Log** — writes full results to `pipeline.log`

### Sample output

```
2026-01-01 [INFO] Pipeline started
2026-01-01 [INFO] Step 1: Scraping playlist...
2026-01-01 [INFO] Extracted 25 song titles
2026-01-01 [INFO] Step 2: Searching YouTube...
2026-01-01 [INFO] Cache hit: Blinding Lights
2026-01-01 [INFO] Found: Save Your Tears → https://youtube.com/watch?v=...
2026-01-01 [INFO] Step 3: Downloading and converting...
2026-01-01 [INFO] Downloaded and converted: Blinding Lights
2026-01-01 [INFO] Pipeline complete. Success: 25 | Failed: 0
```

Your MP3 files will appear in the `output/` folder.

---

## API Quota

The YouTube Data API gives **10,000 units per day** on the free tier. Each search costs **100 units**, so you get **100 searches per day**.

- Results are cached in `cache.json` — re-running never re-searches cached songs
- If quota is hit mid-run, the pipeline stops cleanly and resumes from where it left off next day
- Quota resets at **midnight Pacific Time**

---

## Common Issues

| Error | Fix |
|---|---|
| `YOUTUBE_API_KEY not found` | Check `.env` file has no spaces around `=` |
| `quotaExceeded` | Wait for quota reset at midnight PT, re-run tomorrow |
| CSS selector finds nothing | Re-inspect the page and update the selector in `main.py` |
| FFmpeg not found | Install FFmpeg and ensure it's on your system PATH |
| SSL certificate error (Mac) | Run `/Applications/Python 3.x/Install Certificates.command` |
| Song not found | YouTube search returned no results — song skipped, check log |

---

## Resetting the Cache

To start fresh with a new playlist:

```bash
# Mac/Linux
rm cache.json

# Windows
del cache.json
```

The file will be auto-recreated on the next run.

---

## Disclaimer

This project is intended for personal and educational use only. Downloading YouTube content may violate YouTube's [Terms of Service](https://www.youtube.com/t/terms). Use responsibly and only download content you have the right to access.
