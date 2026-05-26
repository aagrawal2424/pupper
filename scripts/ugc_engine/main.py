"""
Pupper UGC Engine

Modes:
  brief   (default, runs Mon/Wed/Fri) — pick products, generate briefs, submit to Billo or email
  post    — given an approved video URL, post to all platforms with generated captions
"""
import argparse
import json
import os
import tempfile
import urllib.request

from . import config, product_picker, brief_gen, billo


def _send_email(subject: str, html: str) -> None:
    if not config.RESEND_API_KEY:
        print(f"  [email skipped — no RESEND_API_KEY]\n  Subject: {subject}")
        return
    payload = json.dumps({
        "from": "Pupper Alerts <alerts@pupper.com>",
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
            print(f"  Email sent: {json.loads(r.read()).get('id')}")
    except Exception as e:
        print(f"  Email error: {e}")


def run_brief() -> None:
    print("=== Pupper UGC Brief Engine ===")
    n = config.VIDEOS_PER_WEEK
    print(f"\n[1/3] Picking {n} products...")
    products = product_picker.get_products(n)

    if not products:
        print("  No products found (Shopify token may not be configured yet)")
        return

    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{n}] {product['title']}")

        print("  Generating brief...")
        brief = brief_gen.generate_brief(product)

        # Try Billo API first
        result = billo.submit_brief(product, brief)
        if result:
            print(f"  Submitted to Billo: campaign_id={result.get('id')}")
            status = "✓ Submitted to Billo automatically."
        else:
            print("  Billo API not available — sending brief via email")
            status = "📋 Paste this brief into Billo manually."

        # Always email the brief so you have a record
        html = brief_gen.format_brief_email(product, brief)
        html += f"<p><strong>Status:</strong> {status}</p>"
        _send_email(f"UGC Brief: {product['title']} — pupper.com", html)

    print(f"\n✓ {n} briefs generated.")


def run_post(video_url: str, product_handle: str, caption: str) -> None:
    """Download approved UGC video and post to all platforms."""
    print("=== Pupper UGC Post ===")

    # Generate platform captions if not provided
    if not caption:
        caption = f"Our pups tested it. Yours will love it too. 🐾 Link in bio. #pupper #doghealth #dogsupplements #dogsofinstagram #dogmom"

    ig_caption = caption + "\n\n🤖 UGC content — creator compensated."
    fb_caption = caption
    tt_caption = caption[:150] + " #fyp #dogtok #dogvitamins #puppersupplements"
    tw_caption = caption[:200] + f" pupper.com/products/{product_handle}"

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name

    try:
        print(f"Downloading video...")
        urllib.request.urlretrieve(video_url, video_path)

        # Import poster from ugc_engine
        from . import poster
        poster.post_instagram(video_url, ig_caption)
        poster.post_facebook(video_path, fb_caption)
        poster.post_tiktok(video_path, tt_caption)
        poster.post_twitter(video_path, tw_caption)
    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)

    print("\n✓ Posted to all platforms.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="brief", choices=["brief", "post"])
    parser.add_argument("--video-url", default="")
    parser.add_argument("--product-handle", default="")
    parser.add_argument("--caption", default="")
    args = parser.parse_args()

    if args.mode == "post":
        run_post(args.video_url, args.product_handle, args.caption)
    else:
        run_brief()
