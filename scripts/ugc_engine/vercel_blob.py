"""Temporary public audio hosting via transfer.sh — works from CI/CD environments."""
import urllib.request


def upload(filename: str, data: bytes, content_type: str = "audio/mpeg") -> str:
    """Upload audio bytes, return a public URL valid for 1 day."""
    req = urllib.request.Request(
        f"https://transfer.sh/{filename}",
        data=data,
        headers={
            "Content-Type": content_type,
            "Max-Downloads": "20",
            "Max-Days": "1",
        },
        method="PUT",
    )
    with urllib.request.urlopen(req) as r:
        return r.read().decode().strip()
