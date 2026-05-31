"""Generate UGC creator briefs for pupper.com dog supplement products."""
import json
import re
import urllib.request
from . import config

SYSTEM = """You write UGC creator briefs for pupper.com, a premium dog supplement brand.
Briefs are casual, specific, and make it easy for a creator to say yes.
The content must feel real — an actual dog owner sharing how supplements changed their dog's life, not an ad.
The creator's dog MUST be present and visible throughout the entire video."""


def generate_brief(product: dict) -> dict:
    title = product["title"]
    desc = re.sub(r"<[^>]+>", " ", product.get("body_html", "")).strip()[:400]
    price = product["variants"][0]["price"] if product.get("variants") else "39.99"
    url = f"https://pupper.com/products/{product['handle']}"

    prompt = f"""Product: {title}
Price: ${price}
Description: {desc}
URL: {url}

Write a UGC creator brief for a dog owner on Billo. The video should feel like a real person sharing how this supplement genuinely improved their dog's quality of life — better mobility, more energy, shinier coat, calmer behavior, whatever is relevant to this product.

The dog MUST be in every scene. The video should show the dog interacting naturally while the creator talks.

Include:

HOOK: One sentence on the story angle — what transformation will they show? (e.g., "Show us your senior dog moving like they're years younger")
WHAT_TO_SAY: 3-4 bullet points — personal story beats. Should cover: what problem they noticed, when they started Pupper, what changed, and why they'd recommend it. Specific and warm, not salesy.
CREATIVE_DIRECTION: 3 scene ideas that require the dog to be on camera. Examples: "Start with your dog struggling to get up, cut to them running after 30 days", "Hold the Pupper bottle while your dog sniffs it curiously", "Dog in the background playing while you talk to camera about the change you noticed"
DONT: 2-3 things to avoid (e.g., don't show the dog off-screen, don't make it sound scripted, don't focus on product features instead of results)
CAPTION_HOOK: A punchy first line for the social caption — should create curiosity or share a relatable moment

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
        "max_tokens": 900,
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

<h3>Story Hook (use this to attract creators on Billo)</h3>
<p style="background:#f5f5f5;padding:12px;border-left:4px solid #000;">{brief['hook']}</p>

<h3>What to Say (personal story beats)</h3>
<ul>{bullets}</ul>

<h3>Creative Direction (dog must be on camera)</h3>
<p>{brief['creative_direction']}</p>

<h3>Don't Do This</h3>
<ul>{donts}</ul>

<h3>Caption Hook</h3>
<p style="background:#f5f5f5;padding:12px;border-left:4px solid #000;">{brief['caption_hook']}</p>

<p><strong>Target duration:</strong> {brief['estimated_duration']}</p>
<hr>
<p style="color:#999;font-size:12px;">Post on Billo → billo.app. Videos auto-post when delivered via webhook.</p>
"""
