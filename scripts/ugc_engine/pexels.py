"""Fetch vertical dog stock videos from Pexels (free API)."""
import json
import random
import urllib.request
import urllib.parse
import os

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
QUERIES = [
    "dog happy", "puppy playing", "dog running", "dog owner",
    "dog park", "dog healthy", "cute dog", "dog and owner",
]


# Fallback vertical dog videos from Pexels (pre-fetched, always work)
FALLBACK_VIDEOS = [
    "https://videos.pexels.com/video-files/4498037/4498037-uhd_1440_2732_25fps.mp4",
    "https://videos.pexels.com/video-files/4681821/4681821-uhd_1440_2732_25fps.mp4",
    "https://videos.pexels.com/video-files/5732526/5732526-hd_1080_1920_25fps.mp4",
]


def get_video_url(query: str = None) -> str:
    if not PEXELS_KEY:
        print(f"  Pexels: no API key — using fallback video")
        return random.choice(FALLBACK_VIDEOS)

    q = query or random.choice(QUERIES)
    params = urllib.parse.urlencode({"query": q, "orientation": "portrait", "per_page": 15, "size": "medium"})
    req = urllib.request.Request(
        f"https://api.pexels.com/v1/videos/search?{params}",
        headers={"Authorization": PEXELS_KEY},
    )
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"  Pexels error ({e}) — using fallback video")
        return random.choice(FALLBACK_VIDEOS)

    videos = data.get("videos", [])
    if not videos:
        print(f"  Pexels: no results for '{q}' — using fallback video")
        return random.choice(FALLBACK_VIDEOS)

    video = random.choice(videos)
    files = sorted(
        [f for f in video["video_files"] if f.get("height", 0) >= 1080],
        key=lambda f: f.get("height", 0), reverse=True
    )
    if not files:
        files = video["video_files"]

    return files[0]["link"]
