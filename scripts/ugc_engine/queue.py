"""
Video queue — stores approved UGC videos waiting to be posted.
Backed by a JSON file committed to the repo via GitHub API.
Falls back to env var VIDEO_QUEUE_JSON if GitHub API not available.
"""
import json
import os
import base64
import urllib.request
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "ajagrawal452/pupper"
QUEUE_FILE = "video_queue.json"
QUEUE_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{QUEUE_FILE}"


def _gh_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def load_queue() -> list:
    # Try env var first (for testing)
    env_queue = os.environ.get("VIDEO_QUEUE_JSON", "")
    if env_queue:
        return json.loads(env_queue)

    if not GITHUB_TOKEN:
        return []

    try:
        req = urllib.request.Request(QUEUE_API, headers=_gh_headers())
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        content = base64.b64decode(data["content"]).decode()
        return json.loads(content)
    except Exception:
        return []


def save_queue(queue: list) -> None:
    if not GITHUB_TOKEN:
        print("  [queue] No GITHUB_TOKEN — queue not persisted")
        return

    content_b64 = base64.b64encode(json.dumps(queue, indent=2).encode()).decode()

    # Get current SHA if file exists
    sha = None
    try:
        req = urllib.request.Request(QUEUE_API, headers=_gh_headers())
        with urllib.request.urlopen(req) as r:
            sha = json.loads(r.read()).get("sha")
    except Exception:
        pass

    payload = {
        "message": f"Update video queue [{datetime.utcnow().strftime('%Y-%m-%d')}]",
        "content": content_b64,
    }
    if sha:
        payload["sha"] = sha

    req = urllib.request.Request(
        QUEUE_API,
        data=json.dumps(payload).encode(),
        headers={**_gh_headers(), "Content-Type": "application/json"},
        method="PUT",
    )
    urllib.request.urlopen(req)
    print(f"  Queue saved ({len(queue)} videos)")


def add_to_queue(video_url: str, product_handle: str, product_title: str, caption: str) -> None:
    queue = load_queue()
    queue.append({
        "video_url": video_url,
        "product_handle": product_handle,
        "product_title": product_title,
        "caption": caption,
        "added_at": datetime.utcnow().isoformat(),
    })
    save_queue(queue)


def pop_next() -> dict | None:
    queue = load_queue()
    if not queue:
        return None
    item = queue.pop(0)
    save_queue(queue)
    return item
