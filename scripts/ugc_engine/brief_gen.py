"""Generate UGC creator briefs for pupper.com dog supplement products."""
import json
import urllib.request
from . import config

SYSTEM = """You write UGC creator briefs for pupper.com, a premium dog supplement brand.
Briefs are casual, specific, and make it easy for a creator to say yes.
The content should feel real — dog owners talking to other dog owners, not ads."""


def generate_brief(product: dict) -> dict:
    title = product["title"]
    desc = product.get("body_html", "")
    import re
    desc = re.sub(r"<[^>]+>", " ", desc).strip()[:400]
    price = product["variants"][0]["price"] if product.get("variants") else "39.99"
    url = f"https://pupper.com/products/{product['handle']}"

    prompt = f"""Product: {title}
Price: ${price}
Description: {desc}
URL: {url}

Write a UGC brief for a dog owner/creator on Billo. Include:

HOOK: One sentence on why this brief is fun (mention the dog must be in the video)
WHAT_TO_SAY: 3-4 bullet points on key messages (benefits, quality, why their dog loves it)
CREATIVE_DIRECTION: Specific visual/setting instructions — dog must be present, held, or interacting with product. Give 2-3 scene ideas (e.g., "dog on your lap while you talk to camera", "dog sniffing the product", "morning routine with your dog in the background")
DONT: 2-3 things to avoid
CAPTION_HOOK: A punchy first line for the social caption (for the creator to use)

Return as JSON:
{{
  "hook": "...",
  "what_to_say": ["...", "...", "..."],
  "creative_direction": "...",
  "dont": ["...", "..."],
  "caption_hook": "...",
  "estimated_duration": "30-45 seconds"
}}"""

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 800,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as r:
        text = json.loads(r.read())["content"][0]["text"]

    import re
    match = re.search(r"\{[\s\S]+\}", text)
    return json.loads(match.group())


def format_brief_email(product: dict, brief: dict) -> str:
    bullets = "".join(f"<li>{b}</li>" for b in brief["what_to_say"])
    donts = "".join(f"<li>{d}</li>" for d in brief["dont"])
    url = f"https://pupper.com/products/{product['handle']}"

    return f"""
<h2>🐾 New UGC Brief Ready — {product['title']}</h2>
<p><strong>Product URL:</strong> <a href="{url}">{url}</a></p>
<p><strong>Price:</strong> ${product['variants'][0]['price']}</p>

<h3>Brief Hook (paste this to attract creators)</h3>
<p style="background:#f5f5f5;padding:12px;border-left:4px solid #000;">{brief['hook']}</p>

<h3>Key Messages</h3>
<ul>{bullets}</ul>

<h3>Creative Direction</h3>
<p>{brief['creative_direction']}</p>

<h3>Don't Do This</h3>
<ul>{donts}</ul>

<h3>Suggested Caption Hook</h3>
<p style="background:#f5f5f5;padding:12px;border-left:4px solid #000;">{brief['caption_hook']}</p>

<p><strong>Target duration:</strong> {brief['estimated_duration']}</p>
<hr>
<p style="color:#999;font-size:12px;">Post this brief on Billo → billo.app. When the video is delivered, forward it here and I'll post it to all platforms.</p>
"""
