"""
Generate short-form 9:16 videos via Shotstack API.
Combines Pexels dog stock footage, product images, text overlays, music, and optional voiceover.
"""
import json
import os
import time
import urllib.request

SHOTSTACK_KEY = os.environ.get("SHOTSTACK_API_KEY", "")
SHOTSTACK_BASE = "https://api.shotstack.io/v1"

OUTPUT_BASE = {
    "format": "mp4",
    "resolution": "sd",
    "aspectRatio": "9:16",
    "fps": 30,
    "background": "#111111",
}

MUSIC_URL = "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/music/freepd/music.mp3"
UPBEAT_URL = "https://shotstack-assets.s3.ap-southeast-2.amazonaws.com/music/freepd/positive.mp3"


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{SHOTSTACK_BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        raise RuntimeError(f"Shotstack {e.code}: {body_text}")


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


def _render(timeline: dict) -> str:
    resp = _post("/render", {"timeline": timeline, "output": OUTPUT_BASE})
    return _poll(resp["response"]["id"])


def _bg_clip(src: str, length: float, effect: str = "zoomIn", filter_: str = "contrast") -> dict:
    return {
        "asset": {"type": "video", "src": src, "volume": 0},
        "start": 0,
        "length": length,
        "effect": effect,
        "filter": filter_,
    }


def _text_clip(text: str, start: float, length: float, style: str = "chunk",
               size: str = "large", color: str = "#ffffff",
               bg: str = "#000000", position: str = "center",
               transition_in: str = "fade", transition_out: str = "fade") -> dict:
    return {
        "asset": {
            "type": "title",
            "text": text,
            "style": style,
            "color": color,
            "size": size,
            "background": bg,
            "position": position,
        },
        "start": start,
        "length": length,
        "transition": {"in": transition_in, "out": transition_out},
    }


def _audio_clip(src: str, length: float, volume: float = 1.0) -> dict:
    return {
        "asset": {"type": "audio", "src": src, "volume": volume},
        "start": 0,
        "length": length,
    }


# ── Existing templates (unchanged) ────────────────────────────────────────────

def generate_tip_video(headline: str, subtext: str, dog_video_url: str) -> str:
    timeline = {
        "tracks": [
            {"clips": [_bg_clip(dog_video_url, 10)]},
            {"clips": [
                _text_clip(headline, 0.5, 4, size="x-large"),
                _text_clip(subtext, 4.5, 5, size="medium", bg="rgba(0,0,0,0.6)"),
            ]},
        ],
    }
    return _render(timeline)


def generate_product_video(product_title: str, benefit: str, product_img_url: str, dog_video_url: str) -> str:
    timeline = {
        "tracks": [
            {"clips": [_bg_clip(dog_video_url, 12, effect="slideLeft", filter_="muted")]},
            {"clips": [{
                "asset": {"type": "image", "src": product_img_url},
                "start": 1, "length": 10,
                "position": "center", "scale": 0.55,
                "transition": {"in": "slideUp", "out": "fade"},
            }]},
            {"clips": [
                _text_clip(product_title, 1.5, 10, size="large", position="top"),
                _text_clip(benefit + "\n\nLink in bio 🐾", 3, 8, size="small",
                           bg="rgba(0,0,0,0.7)", position="bottom"),
            ]},
        ],
    }
    return _render(timeline)


# ── New templates ──────────────────────────────────────────────────────────────

def generate_voiceover_tip_video(tip: dict, audio_url: str, dog_video_url: str) -> str:
    """Narrated dog health tip — ElevenLabs voiceover with text on dark background."""
    duration = 21.0
    timeline = {
        "tracks": [
            {"clips": [
                _text_clip(tip["hook"], 0.5, 6.0, style="chunk", size="x-large",
                           position="center", transition_in="fade", transition_out="fade"),
                _text_clip(tip["body"], 6.5, 11.0, style="subtitle", size="small",
                           color="#ffffff", bg="rgba(0,0,0,0.75)", position="bottom",
                           transition_in="fade", transition_out="fade"),
                _text_clip("pupper.com 🐾", 18.5, 2.0, style="chunk", size="medium",
                           bg="rgba(0,0,0,0.9)", position="center",
                           transition_in="fade", transition_out="fade"),
            ]},
            # Voiceover audio
            {"clips": [_audio_clip(audio_url, duration)]},
        ],
    }
    return _render(timeline)


def generate_product_story_video(product_title: str, benefit: str, product_img_url: str,
                                  audio_url: str, dog_video_url: str) -> str:
    """Product deep-dive with ElevenLabs narration and product image on dark background."""
    duration = 22.0
    timeline = {
        "tracks": [
            # Product image — slides in and holds center stage
            {"clips": [{
                "asset": {"type": "image", "src": product_img_url},
                "start": 4.0, "length": 14.0,
                "position": "center", "scale": 0.5,
                "transition": {"in": "slideUp", "out": "fade"},
            }]},
            {"clips": [
                _text_clip(product_title, 0.5, 5.0, style="chunk", size="x-large",
                           position="center", transition_in="fade"),
                _text_clip(benefit, 4.5, 13.0, style="subtitle", size="small",
                           color="#ffffff", bg="rgba(0,0,0,0.8)", position="bottom",
                           transition_in="fade", transition_out="fade"),
                _text_clip("Link in bio 🐾  pupper.com", 19.0, 2.5, style="chunk",
                           size="medium", bg="rgba(0,0,0,0.9)", position="center",
                           transition_in="fade", transition_out="fade"),
            ]},
            {"clips": [_audio_clip(audio_url, duration)]},
        ],
    }
    return _render(timeline)


def generate_relatable_reel(moment: dict, dog_video_url: str) -> str:
    """Text-on-screen relatable dog parent moment — text on dark background."""
    lines = moment["lines"]
    duration = 13.0
    segment = duration / len(lines)

    text_clips = []
    for i, line in enumerate(lines):
        start = i * segment + 0.3
        length = segment - 0.6
        text_clips.append(
            _text_clip(line, start, length, style="chunk", size="large",
                       color="#ffffff", bg="rgba(0,0,0,0.85)", position="center",
                       transition_in="fade", transition_out="fade")
        )

    timeline = {"tracks": [{"clips": text_clips}]}
    return _render(timeline)


def generate_ingredient_spotlight_video(ingredient: dict, audio_url: str, dog_video_url: str) -> str:
    """Hero ingredient education — name reveal, benefit, science fact, CTA, with narration."""
    duration = 22.0
    timeline = {
        "tracks": [
            {"clips": [
                # Big ingredient name reveal
                _text_clip(ingredient["name"], 0.5, 5.0, style="chunk", size="x-large",
                           color="#ffffff", bg="#000000", position="center",
                           transition_in="fade", transition_out="fade"),
                # Benefit
                _text_clip(ingredient["benefit"], 5.5, 6.0, style="chunk", size="medium",
                           color="#ffffff", bg="rgba(0,0,0,0.8)", position="center",
                           transition_in="fade", transition_out="fade"),
                # Science fact
                _text_clip(f"🔬 {ingredient['fact']}", 11.5, 6.5, style="subtitle", size="small",
                           color="#ffffff", bg="rgba(0,0,0,0.85)", position="bottom",
                           transition_in="fade", transition_out="fade"),
                # CTA
                _text_clip(ingredient["cta"], 18.5, 3.0, style="chunk", size="small",
                           color="#ffffff", bg="#000000", position="center",
                           transition_in="fade", transition_out="fade"),
            ]},
            {"clips": [_audio_clip(audio_url, duration)]},
        ],
    }
    return _render(timeline)


def generate_social_proof_video(quote: str, product_title: str,
                                 audio_url: str, dog_video_url: str) -> str:
    """Animated customer review with voiceover on dark background."""
    duration = 17.0
    timeline = {
        "tracks": [
            {"clips": [
                _text_clip("Real dog owners. Real results. 🐾", 0.5, 4.0,
                           style="chunk", size="large", bg="#000000", position="center",
                           transition_in="fade", transition_out="fade"),
                _text_clip(f'"{quote}"', 4.5, 9.0, style="subtitle", size="small",
                           color="#ffffff", bg="rgba(0,0,0,0.85)", position="center",
                           transition_in="fade", transition_out="fade"),
                _text_clip(f"{product_title}\npupper.com 🐾", 14.0, 2.5,
                           style="chunk", size="medium", bg="#000000", position="center",
                           transition_in="fade", transition_out="fade"),
            ]},
            {"clips": [_audio_clip(audio_url, duration)]},
        ],
    }
    return _render(timeline)
