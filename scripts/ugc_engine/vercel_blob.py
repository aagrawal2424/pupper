"""
Temporary audio hosting via GitHub repo + raw.githubusercontent.com CDN.
Overwrites a single tmp file each run — repo is public so no auth needed to read.
"""
import base64
import json
import os
import urllib.request

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "aagrawal2424/pupper"
AUDIO_PATH = "tmp/voiceover.mp3"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{AUDIO_PATH}"


def _gh_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def upload(filename: str, data: bytes, content_type: str = "audio/mpeg") -> str:
    """Upload audio to GitHub repo, return public raw CDN URL."""
    sha = None
    try:
        req = urllib.request.Request(API_URL, headers=_gh_headers())
        with urllib.request.urlopen(req) as r:
            sha = json.loads(r.read()).get("sha")
    except Exception:
        pass

    payload = {
        "message": "tmp: update voiceover audio [skip ci]",
        "content": base64.b64encode(data).decode(),
    }
    if sha:
        payload["sha"] = sha

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={**_gh_headers(), "Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req) as r:
        json.loads(r.read())

    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{AUDIO_PATH}"
    print(f"  Audio hosted: {url}")
    return url
