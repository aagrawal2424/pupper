"""ElevenLabs text-to-speech — returns MP3 bytes from a voiceover script."""
import json
import urllib.request
from . import config

BASE = "https://api.elevenlabs.io/v1"


def text_to_speech(text: str) -> bytes:
    if not config.ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set")
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
            "style": 0.35,
            "use_speaker_boost": True,
        },
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/text-to-speech/{config.ELEVENLABS_VOICE_ID}",
        data=payload,
        headers={
            "xi-api-key": config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    with urllib.request.urlopen(req) as r:
        return r.read()
