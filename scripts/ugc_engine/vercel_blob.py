"""Temporary public audio hosting via file.io — no setup required."""
import json
import urllib.request


def upload(filename: str, data: bytes, content_type: str = "audio/mpeg") -> str:
    """Upload audio bytes, return a public URL valid for 30 minutes."""
    boundary = "pupper_audio_boundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        "https://file.io/?expires=30m&maxdownloads=10",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())

    if not result.get("success"):
        raise RuntimeError(f"file.io upload failed: {result}")

    return result["link"]
