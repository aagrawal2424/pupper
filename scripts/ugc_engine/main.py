"""
Pupper Social Engine — fully automated daily posting pipeline.

Modes:
  daily   (default) — posts today's content based on day of week
  brief   — sends UGC briefs to Billo (runs Mon/Wed separately)
"""
import argparse
import json
import os
import tempfile
import time
import urllib.request
from datetime import datetime

from . import config, product_picker, brief_gen, billo, pexels, shotstack
from . import queue, scheduler, poster, elevenlabs, vercel_blob


def _claude(prompt: str, max_tokens: int = 200) -> str:
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": max_tokens,
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
        return json.loads(r.read())["content"][0]["text"].strip()


def _generate_voiceover(script: str) -> str:
    """Generate ElevenLabs MP3, upload to Vercel Blob, return public URL."""
    audio_bytes = elevenlabs.text_to_speech(script)
    filename = f"pupper-vo-{int(time.time())}.mp3"
    url = vercel_blob.upload(filename, audio_bytes)
    print(f"  Voiceover uploaded: {url[:60]}...")
    return url


def _send_email(subject: str, html: str) -> None:
    if not config.RESEND_API_KEY:
        print(f"  [email skipped] {subject}")
        return
    payload = json.dumps({
        "from": "Pupper <alerts@pupper.com>",
        "to": [config.ADMIN_EMAIL],
        "subject": subject,
        "html": html,
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails", data=payload,
        headers={"Authorization": f"Bearer {config.RESEND_API_KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            print(f"  Email: {json.loads(r.read()).get('id')}")
    except Exception as e:
        print(f"  Email error: {e}")


def _post_to_platforms(video_url: str, video_path: str, caption: str, tiktok_caption: str = None) -> None:
    poster.post_instagram(video_url, caption)
    poster.post_tiktok(video_path, tiktok_caption or caption)


# ── Content handlers ───────────────────────────────────────────────────────────

def _post_ugc(video_path: str) -> None:
    item = queue.pop_next()
    if not item:
        print("  No UGC in queue — falling back to product story")
        _post_product_story(video_path)
        return

    print(f"  UGC: {item['product_title']}")
    urllib.request.urlretrieve(item["video_url"], video_path)
    tag = "#pupper #doghealth #dogsupplements #dogsofinstagram #dogmom #realresults"
    caption = item.get("caption", f"Real results for real dogs. 🐾 #pupper #doghealth")
    _post_to_platforms(
        item["video_url"], video_path,
        f"{caption}\n\n{tag}",
        f"{caption} #fyp #dogtok #dogvitamins #puppersupplements",
    )
    print("  ✓ UGC posted")


def _post_voiceover_tip(video_path: str) -> None:
    tip = scheduler.get_tip()
    print(f"  Tip: {tip['hook']}")

    script = _claude(
        f"Write a 20-second TikTok/Instagram Reels voiceover script for Pupper, a premium dog supplement brand.\n"
        f"Topic: {tip['hook']}\n"
        f"Key message: {tip['body']}\n"
        f"Tone: warm, direct, conversational — like a knowledgeable dog parent talking to another dog parent.\n"
        f"Hook hard in the first sentence. No more than 65 words. Output only the script, no quotes."
    )
    print(f"  Script: {script[:60]}...")

    audio_url = _generate_voiceover(script)
    dog_url = pexels.get_video_url(tip["search"])
    video_url = shotstack.generate_voiceover_tip_video(tip, audio_url, dog_url)

    urllib.request.urlretrieve(video_url, video_path)
    tag = "#pupper #doghealth #dogsupplements #dogtips #dogmom #dogsofinstagram"
    _post_to_platforms(
        video_url, video_path,
        f"{tip['caption']}\n\n{tag}",
        f"{tip['caption']} #fyp #dogtok #dogparent #dogsupplements",
    )
    print("  ✓ Voiceover tip posted")


def _post_product_story(video_path: str) -> None:
    products = product_picker.get_products(1)
    if not products:
        print("  No products — skipping product story")
        return

    product = products[0]
    img_url = product["images"][0]["src"] if product.get("images") else ""
    if not img_url:
        print("  Product has no image — skipping")
        return

    import re
    desc = re.sub(r"<[^>]+>", " ", product.get("body_html", "")).strip()
    benefit_text = (desc[:200] + "...") if len(desc) > 200 else desc

    print(f"  Product story: {product['title']}")

    script = _claude(
        f"Write a 20-second TikTok/Instagram Reels voiceover script for this Pupper dog supplement.\n"
        f"Product: {product['title']}\n"
        f"Key benefit: {benefit_text}\n"
        f"Lead with a problem the dog owner feels. Then introduce the product as the solution. "
        f"End with 'Link in bio'. Warm, direct, not salesy. No more than 65 words. Output only the script."
    )
    print(f"  Script: {script[:60]}...")

    audio_url = _generate_voiceover(script)
    dog_url = pexels.get_video_url("dog owner happy")
    video_url = shotstack.generate_product_story_video(
        product["title"], benefit_text[:120], img_url, audio_url, dog_url
    )

    urllib.request.urlretrieve(video_url, video_path)
    caption = f"Your dog deserves this. 🐾 {product['title']} — link in bio."
    tag = "#pupper #dogsupplements #doghealth #dogmom #dogsofinstagram"
    _post_to_platforms(
        video_url, video_path,
        f"{caption}\n\n{tag}",
        f"{caption} #fyp #dogtok #dogvitamins #puppersupplements",
    )
    print("  ✓ Product story posted")


def _post_relatable_reel(video_path: str) -> None:
    moment = scheduler.get_relatable_moment()
    print(f"  Relatable: {moment['lines'][0]}")

    dog_url = pexels.get_video_url(moment["search"])
    video_url = shotstack.generate_relatable_reel(moment, dog_url)

    urllib.request.urlretrieve(video_url, video_path)
    tag = "#pupper #doglife #dogmom #dogsofinstagram #dogparent"
    _post_to_platforms(
        video_url, video_path,
        f"{moment['caption']}\n\n{tag}",
        f"{moment['caption']} #fyp #dogtok #doghumor #dogviral",
    )
    print("  ✓ Relatable reel posted")


def _post_ingredient_spotlight(video_path: str) -> None:
    ingredient = scheduler.get_ingredient()
    print(f"  Ingredient: {ingredient['name']}")

    script = _claude(
        f"Write a 20-second TikTok/Instagram Reels voiceover about {ingredient['name']} for Pupper dog supplements.\n"
        f"Key benefit: {ingredient['benefit']}\n"
        f"Science fact to include: {ingredient['fact']}\n"
        f"End with this CTA: {ingredient['cta']}\n"
        f"Tone: credible, warm, educational — like a vet friend explaining it simply. "
        f"No more than 65 words. Output only the script."
    )
    print(f"  Script: {script[:60]}...")

    audio_url = _generate_voiceover(script)
    dog_url = pexels.get_video_url(ingredient["search"])
    video_url = shotstack.generate_ingredient_spotlight_video(ingredient, audio_url, dog_url)

    urllib.request.urlretrieve(video_url, video_path)
    caption = f"The science behind why {ingredient['name']} works 🐾 Link in bio."
    tag = "#pupper #dogscience #dogsupplements #doghealth #dogmom #dogsofinstagram"
    _post_to_platforms(
        video_url, video_path,
        f"{caption}\n\n{tag}",
        f"{caption} #fyp #dogtok #dognutrition #learnontiktok",
    )
    print("  ✓ Ingredient spotlight posted")


def _post_social_proof(video_path: str) -> None:
    scenario = scheduler.get_social_proof_scenario()
    print(f"  Social proof: {scenario['product_type']}")

    # Generate a realistic customer testimonial via Claude
    quote = _claude(
        f"Write a single authentic-sounding customer testimonial quote (1-2 sentences, no more than 35 words) "
        f"from a real dog owner about Pupper {scenario['product_type']}. "
        f"The story angle: {scenario['angle']}. "
        f"First person, specific detail, no marketing language. Output only the quote, no attribution."
    )

    script = _claude(
        f"Write a 15-second TikTok voiceover for Pupper dog supplements presenting this customer story:\n"
        f'"{quote}"\n'
        f"Frame it as 'here\'s what real dog owners are saying about Pupper...' "
        f"Warm and believable. End with 'pupper.com'. No more than 50 words. Output only the script."
    )
    print(f"  Script: {script[:60]}...")

    # Get the matching product name from Shopify if available, else use type
    products = product_picker.get_products(1)
    product_title = products[0]["title"] if products else f"Pupper {scenario['product_type'].title()}"

    audio_url = _generate_voiceover(script)
    dog_url = pexels.get_video_url(scenario["search"])
    video_url = shotstack.generate_social_proof_video(quote, product_title, audio_url, dog_url)

    urllib.request.urlretrieve(video_url, video_path)
    caption = f"This is why we do what we do 🐾 Real dogs. Real results. Link in bio."
    tag = "#pupper #dogsupplements #doghealth #dogmom #realresults #dogsofinstagram"
    _post_to_platforms(
        video_url, video_path,
        f"{caption}\n\n{tag}",
        f"{caption} #fyp #dogtok #dogresults #puppersupplements",
    )
    print("  ✓ Social proof posted")


# ── Entry points ───────────────────────────────────────────────────────────────

HANDLERS = {
    "ugc": _post_ugc,
    "voiceover_tip": _post_voiceover_tip,
    "product_story": _post_product_story,
    "relatable_reel": _post_relatable_reel,
    "ingredient_spotlight": _post_ingredient_spotlight,
    "social_proof": _post_social_proof,
}


def run_daily() -> None:
    print(f"=== Pupper Daily Post — {datetime.utcnow().strftime('%A %Y-%m-%d')} ===")
    content_type = scheduler.today_content_type()
    print(f"Content type: {content_type}")

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name

    try:
        HANDLERS[content_type](video_path)
    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)


def run_brief() -> None:
    print("=== Pupper UGC Brief Engine ===")
    n = config.VIDEOS_PER_WEEK
    print(f"Briefing {n} products...")
    products = product_picker.get_products(n)

    if not products:
        print("  No products (Shopify not configured yet)")
        return

    for product in products:
        print(f"  Generating brief: {product['title']}")
        brief = brief_gen.generate_brief(product)
        result = billo.submit_brief(product, brief)
        if result:
            print(f"  → Billo: {result.get('id')}")
        html = brief_gen.format_brief_email(product, brief)
        status = "✓ Submitted to Billo." if result else "📋 Paste into Billo manually."
        html += f"<p><strong>Status:</strong> {status}</p>"
        _send_email(f"UGC Brief: {product['title']}", html)

    print(f"✓ {n} briefs sent.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="daily", choices=["daily", "brief"])
    args = parser.parse_args()

    if args.mode == "brief":
        run_brief()
    else:
        run_daily()
