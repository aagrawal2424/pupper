"""Upload bytes to Vercel Blob for temporary public hosting (used by Shotstack)."""
import json
import urllib.parse
import urllib.request
from . import config


def upload(filename: str, data: bytes, content_type: str = "audio/mpeg") -> str:
    if not config.VERCEL_BLOB_TOKEN:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN not set")
    req = urllib.request.Request(
        f"https://blob.vercel-storage.com/{urllib.parse.quote(filename)}",
        data=data,
        headers={
            "Authorization": f"Bearer {config.VERCEL_BLOB_TOKEN}",
            "Content-Type": content_type,
            "x-add-random-suffix": "1",
        },
        method="PUT",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["url"]
