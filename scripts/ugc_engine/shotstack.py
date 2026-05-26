"""
Generate short-form 9:16 videos via Shotstack API.
Combines Pexels dog stock footage + product image + text overlay + music.
"""
import json
import os
import time
import urllib.request

SHOTSTACK_KEY = os.environ.get("SHOTSTACK_API_KEY", "")
SHOTSTACK_BASE = "https://api.shotstack.io/stage/v1"  # use 'v1' for prod


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{SHOTSTACK_BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _get(path: str) -> dict:
    req = urllib.request.Request(
        f"{SHOTSTACK_BASE}{path}",
        headers={"x-api-key": SHOTSTACK_KEY},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _poll(render_id: str, timeout: int = 300) -> str:
    for _ in range(timeout // 5):
        time.sleep(5)
        resp = _get(f"/render/{render_id}")
        status = resp["response"]["status"]
        print(f"  Shotstack: {status}")
        if status == "done":
            return resp["response"]["url"]
        if status == "failed":
            raise RuntimeError(f"Shotstack render failed: {resp['response'].get('error')}")
    raise TimeoutError("Shotstack render timed out")


def _music_track() -> dict:
    """Royalty-free upbeat background music."""
    return {
        "src": "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/music/freepd/music.mp3",
        "effect": "fadeInFadeOut",
        "volume": 0.15,
    }


def generate_tip_video(headline: str, subtext: str, dog_video_url: str) -> str:
    """Dog health tip: stock footage + bold text overlay."""
    timeline = {
        "soundtrack": _music_track(),
        "tracks": [
            {
                "clips": [{
                    "asset": {"type": "video", "src": dog_video_url, "volume": 0},
                    "start": 0, "length": 10,
                    "effect": "zoomIn",
                    "filter": "contrast",
                }]
            },
            {
                "clips": [
                    {
                        "asset": {
                            "type": "title",
                            "text": headline,
                            "style": "chunk",
                            "color": "#ffffff",
                            "size": "x-large",
                            "background": "#000000",
                            "position": "center",
                        },
                        "start": 0.5, "length": 4,
                        "transition": {"in": "fadeIn", "out": "fadeOut"},
                    },
                    {
                        "asset": {
                            "type": "title",
                            "text": subtext,
                            "style": "chunk",
                            "color": "#ffffff",
                            "size": "medium",
                            "background": "rgba(0,0,0,0.6)",
                            "position": "center",
                        },
                        "start": 4.5, "length": 5,
                        "transition": {"in": "fadeIn", "out": "fadeOut"},
                    },
                ]
            },
        ],
    }
    output = {
        "format": "mp4",
        "resolution": "sd",
        "aspectRatio": "9:16",
        "fps": 30,
    }
    resp = _post("/render", {"timeline": timeline, "output": output})
    render_id = resp["response"]["id"]
    return _poll(render_id)


def generate_product_video(product_title: str, benefit: str, product_img_url: str, dog_video_url: str) -> str:
    """Product spotlight: dog stock bg + product image + text."""
    timeline = {
        "soundtrack": _music_track(),
        "tracks": [
            {
                "clips": [{
                    "asset": {"type": "video", "src": dog_video_url, "volume": 0},
                    "start": 0, "length": 12,
                    "effect": "slideLeft",
                    "filter": "muted",
                }]
            },
            {
                "clips": [{
                    "asset": {
                        "type": "image",
                        "src": product_img_url,
                    },
                    "start": 1, "length": 10,
                    "position": "center",
                    "scale": 0.55,
                    "transition": {"in": "slideUp", "out": "fadeOut"},
                }]
            },
            {
                "clips": [
                    {
                        "asset": {
                            "type": "title",
                            "text": product_title,
                            "style": "chunk",
                            "color": "#ffffff",
                            "size": "large",
                            "background": "#000000",
                            "position": "top",
                        },
                        "start": 1.5, "length": 10,
                    },
                    {
                        "asset": {
                            "type": "title",
                            "text": benefit + "\n\nLink in bio 🐾",
                            "style": "chunk",
                            "color": "#ffffff",
                            "size": "small",
                            "background": "rgba(0,0,0,0.7)",
                            "position": "bottom",
                        },
                        "start": 3, "length": 8,
                        "transition": {"in": "fadeIn"},
                    },
                ]
            },
        ],
    }
    output = {"format": "mp4", "resolution": "sd", "aspectRatio": "9:16", "fps": 30}
    resp = _post("/render", {"timeline": timeline, "output": output})
    return _poll(resp["response"]["id"])
