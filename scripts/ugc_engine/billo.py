"""
Billo API integration.
If BILLO_API_KEY is set, submits briefs programmatically.
If not, falls back to email-only mode (you paste the brief into Billo manually).
"""
import json
import urllib.request
from . import config

BILLO_API_BASE = "https://api.billo.app/v1"


def submit_brief(product: dict, brief: dict) -> dict | None:
    """Submit a UGC brief to Billo. Returns campaign data or None if API unavailable."""
    if not config.BILLO_API_KEY:
        return None

    payload = json.dumps({
        "campaign_name": f"Pupper — {product['title']}",
        "product_name": product["title"],
        "product_url": f"https://pupper.com/products/{product['handle']}",
        "product_price": product["variants"][0]["price"] if product.get("variants") else "39.99",
        "brief": {
            "hook": brief["hook"],
            "key_messages": brief["what_to_say"],
            "creative_direction": brief["creative_direction"],
            "restrictions": brief["dont"],
            "video_duration": brief["estimated_duration"],
        },
        "video_count": 1,
        "content_type": "ugc_video",
    }).encode()

    req = urllib.request.Request(
        f"{BILLO_API_BASE}/campaigns",
        data=payload,
        headers={
            "Authorization": f"Bearer {config.BILLO_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  Billo API error: {e} — falling back to email mode")
        return None
