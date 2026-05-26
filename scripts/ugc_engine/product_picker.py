"""Pick products to brief this week, avoiding recently briefed ones."""
import json
import os
import random
import urllib.request
from . import config

BRIEFED_CACHE = os.path.join(os.path.dirname(__file__), "../../.briefed_cache.json")


def _load_cache() -> list:
    if os.path.exists(BRIEFED_CACHE):
        return json.load(open(BRIEFED_CACHE))
    return []


def _save_cache(handles: list) -> None:
    # Keep last 20 to avoid re-briefing recently
    json.dump(handles[-20:], open(BRIEFED_CACHE, "w"))


def get_products(n: int = 3) -> list:
    if not config.SHOPIFY_TOKEN:
        return []

    req = urllib.request.Request(
        f"https://{config.SHOPIFY_STORE}/admin/api/2025-01/products.json"
        "?limit=250&status=active&fields=id,title,body_html,handle,images,variants",
        headers={"X-Shopify-Access-Token": config.SHOPIFY_TOKEN},
    )
    with urllib.request.urlopen(req) as r:
        products = json.loads(r.read())["products"]

    skip = {"bundle", "gift", "free"}
    eligible = [
        p for p in products
        if p.get("images")
        and not any(s in p["title"].lower() for s in skip)
    ]

    briefed = _load_cache()
    fresh = [p for p in eligible if p["handle"] not in briefed]
    if len(fresh) < n:
        fresh = eligible  # reset cycle if we've gone through all

    picks = random.sample(fresh, min(n, len(fresh)))
    _save_cache(briefed + [p["handle"] for p in picks])
    return picks
