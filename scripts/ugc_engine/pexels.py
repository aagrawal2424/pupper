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


def get_video_url(query: str = None) -> str:
    if not PEXELS_KEY:
        raise RuntimeError("PEXELS_API_KEY not set")

    q = query or random.choice(QUERIES)
    params = urllib.parse.urlencode({"query": q, "orientation": "portrait", "per_page": 15, "size": "medium"})
    req = urllib.request.Request(
        f"https://api.pexels.com/v1/videos/search?{params}",
        headers={"Authorization": PEXELS_KEY},
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())

    videos = data.get("videos", [])
    if not videos:
        raise RuntimeError(f"No Pexels videos found for: {q}")

    video = random.choice(videos)
    # Pick highest quality portrait file
    files = sorted(
        [f for f in video["video_files"] if f.get("height", 0) >= 1080],
        key=lambda f: f.get("height", 0), reverse=True
    )
    if not files:
        files = video["video_files"]

    return files[0]["link"]
