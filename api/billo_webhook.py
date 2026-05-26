"""
Vercel serverless function — receives Billo video delivery webhooks.

When a creator delivers a video on Billo, Billo POSTs here.
This adds the video to the GitHub-backed queue so the daily
GitHub Actions job picks it up automatically.

Deploy: vercel deploy --prod (from pupper repo root)
Set env vars: BILLO_WEBHOOK_SECRET, GITHUB_TOKEN
"""
import base64
import hashlib
import hmac
import json
import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "ajagrawal452/pupper"
QUEUE_FILE = "video_queue.json"
QUEUE_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{QUEUE_FILE}"
BILLO_WEBHOOK_SECRET = os.environ.get("BILLO_WEBHOOK_SECRET", "")


def _gh_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _load_queue():
    try:
        req = urllib.request.Request(QUEUE_API, headers=_gh_headers())
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        content = base64.b64decode(data["content"]).decode()
        return json.loads(content), data.get("sha")
    except Exception:
        return [], None


def _save_queue(queue: list, sha: str | None) -> None:
    content_b64 = base64.b64encode(json.dumps(queue, indent=2).encode()).decode()
    payload = {
        "message": f"Add video to queue [{time.strftime('%Y-%m-%d')}]",
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


def _verify_signature(body: bytes, signature: str) -> bool:
    if not BILLO_WEBHOOK_SECRET:
        return True
    expected = "sha256=" + hmac.new(
        BILLO_WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _parse_billo_payload(data: dict) -> dict | None:
    """Extract the fields we need regardless of Billo payload shape."""
    # Billo may wrap in data.video or at the top level
    video = data.get("data", data)

    video_url = (
        video.get("video_url")
        or video.get("video", {}).get("url")
        or video.get("download_url")
    )
    if not video_url:
        return None

    product = video.get("product") or video.get("campaign") or {}
    product_title = product.get("title") or video.get("campaign_name") or "Pupper Product"
    product_handle = product.get("handle") or product.get("slug") or ""

    creator = video.get("creator") or {}
    creator_handle = creator.get("handle") or creator.get("username") or "creator"

    caption = (
        video.get("caption")
        or f"Real results for real dogs. 🐾 #pupper #dogsupplements #doghealth"
    )

    return {
        "video_url": video_url,
        "product_handle": product_handle,
        "product_title": product_title,
        "caption": caption,
        "creator": creator_handle,
        "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        sig = self.headers.get("X-Billo-Signature", "")
        if not _verify_signature(body, sig):
            self._respond(401, {"error": "invalid signature"})
            return

        try:
            data = json.loads(body)
        except Exception:
            self._respond(400, {"error": "invalid JSON"})
            return

        item = _parse_billo_payload(data)
        if not item:
            self._respond(400, {"error": "missing video_url"})
            return

        if not GITHUB_TOKEN:
            self._respond(500, {"error": "GITHUB_TOKEN not configured"})
            return

        queue, sha = _load_queue()
        queue.append(item)
        _save_queue(queue, sha)

        print(f"Queued: {item['product_title']} — {item['video_url']}")
        self._respond(200, {"ok": True, "queued": item["product_title"], "queue_length": len(queue)})

    def do_GET(self):
        queue, _ = _load_queue()
        self._respond(200, {"queue_length": len(queue), "status": "ok"})

    def _respond(self, code: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
