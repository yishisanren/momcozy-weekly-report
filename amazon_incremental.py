#!/usr/bin/env python3
"""Quota-aware Momcozy Amazon incremental collector.

Designed for unattended cron:
- never uses Canopy as a search engine
- reads a fixed ASIN whitelist
- enforces a small per-run request budget
- stops pagination as soon as already-seen reviews appear
- works in dry-run/plan mode when CANOPY_API_KEY is absent
"""

import hashlib
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

ROOT = Path("/Users/zhangweiwei/momcozy-weekly-report")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(ROOT / ".env")
AMZ = ROOT / "data" / "amazon"
TODAY = date.today().isoformat()
OUTDIR = AMZ / "weekly" / TODAY
STATE_PATH = AMZ / "state.json"
CANOPY_BASE = "https://rest.canopyapi.co/api/amazon"
DOMAIN = os.getenv("AMAZON_DOMAIN", "US")
MAX_REQUESTS = int(os.getenv("AMAZON_CANOPY_WEEKLY_BUDGET", "8"))
TIMEOUT = int(os.getenv("AMAZON_CANOPY_TIMEOUT", "55"))

def parse_api_keys() -> list[str]:
    raw_values = [
        os.getenv("CANOPY_API_KEYS", ""),
        os.getenv("CANOPY_API_KEY", ""),
        os.getenv("CANOPY_APIKEY", ""),
        os.getenv("CANOPY_API_KEY_US", ""),
    ]
    keys: list[str] = []
    for raw in raw_values:
        for item in raw.replace(";", ",").split(","):
            key = item.strip()
            if key and key not in keys:
                keys.append(key)
    return keys


API_KEYS = parse_api_keys()

# User-confirmed whitelist. Keep this as the source of truth for the cron job.
ASINS = [
    {"tier": "P0", "line": "吸奶器", "model": "M5 Smart", "asin": "B0F7XTHCNY", "mode": "reviews"},
    {"tier": "P0", "line": "吸奶器", "model": "M9", "asin": "B0CGXMJF8S", "mode": "reviews"},
    {"tier": "P0", "line": "吸奶器", "model": "Air 1", "asin": "B0DBYF4Z6L", "mode": "reviews"},
    {"tier": "P0", "line": "睡眠线", "model": "BM04", "asin": "B0DR18KGBW", "mode": "reviews"},
    {"tier": "P0", "line": "睡眠线", "model": "BM08", "asin": "B0GJ8HDZ29", "mode": "reviews"},
    {"tier": "P0", "line": "睡眠线", "model": "T31", "asin": "B0FXGTGQG7", "mode": "reviews"},
    {"tier": "P1", "line": "睡眠线", "model": "Baby Sound Machine", "asin": "B099RSXLGH", "mode": "product_then_maybe_reviews"},
    {"tier": "P1", "line": "睡眠线", "model": "Baby Sound Machine", "asin": "B0D5CY5P9K", "mode": "product_then_maybe_reviews"},
    {"tier": "P1", "line": "睡眠线", "model": "Baby Sound Machine", "asin": "B0D5CYDF9T", "mode": "product_then_maybe_reviews"},
]
UNLISTED = [
    {"line": "吸奶器", "model": "M10", "status": "暂时未上架"},
    {"line": "睡眠线", "model": "BM04M/BM05", "status": "暂时未上架"},
]


def load_state() -> Dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"asins": {}, "runs": []}


def save_state(state: Dict[str, Any]) -> None:
    AMZ.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def review_key(review: Dict[str, Any], asin: str) -> str:
    explicit = review.get("id") or review.get("reviewId") or review.get("review_id")
    if explicit:
        return str(explicit)
    raw = "|".join(
        str(review.get(k, ""))
        for k in ["rating", "title", "body", "text", "content", "date", "reviewDate"]
    )
    return hashlib.sha1((asin + "|" + raw).encode("utf-8", "ignore")).hexdigest()


def canopy_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if not API_KEYS:
        raise RuntimeError("CANOPY_API_KEYS/CANOPY_API_KEY not found; dry-run only")
    last_error = None
    exhausted = []
    for key_index, api_key in enumerate(API_KEYS, start=1):
        headers = {"API-KEY": api_key, "User-Agent": "Hermes Momcozy Amazon incremental collector"}
        for attempt in range(2):
            try:
                r = requests.get(f"{CANOPY_BASE}/{path}", headers=headers, params=params, timeout=TIMEOUT)
                if r.status_code in {401, 402, 403, 429}:
                    exhausted.append(f"key#{key_index}:{r.status_code}")
                    last_error = requests.HTTPError(f"Canopy key#{key_index} returned {r.status_code}")
                    break
                r.raise_for_status()
                return r.json()
            except Exception as e:  # bounded retry only
                last_error = e
                if attempt == 0:
                    time.sleep(2)
    if exhausted:
        raise RuntimeError("All Canopy keys unavailable: " + ", ".join(exhausted))
    raise RuntimeError(str(last_error))


def extract_product(payload: Dict[str, Any]) -> Dict[str, Any]:
    product = payload.get("data", {}).get("amazonProduct") or payload.get("amazonProduct") or payload.get("product") or payload
    return {
        "title": product.get("title") or product.get("name"),
        "rating": product.get("rating") or product.get("ratingScore"),
        "ratings_total": product.get("ratingsTotal") or product.get("reviewCount") or product.get("ratingsCount"),
        "url": product.get("url"),
    }


def extract_reviews(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    product = payload.get("data", {}).get("amazonProduct") or payload.get("amazonProduct") or payload
    paged = product.get("reviewsPaginated") or payload.get("reviewsPaginated") or {}
    reviews = paged.get("reviews") or product.get("topReviews") or payload.get("reviews") or []
    page_info = paged.get("pageInfo") or payload.get("pageInfo") or {}
    return reviews, page_info


def normalize_review(raw: Dict[str, Any], item: Dict[str, str]) -> Dict[str, Any]:
    body = raw.get("body") or raw.get("text") or raw.get("content") or raw.get("review") or ""
    title = raw.get("title") or raw.get("headline") or ""
    return {
        "asin": item["asin"],
        "model": item["model"],
        "line": item["line"],
        "domain": DOMAIN,
        "review_key": review_key(raw, item["asin"]),
        "rating": raw.get("rating") or raw.get("score"),
        "title": title,
        "body": body,
        "date": raw.get("date") or raw.get("reviewDate") or raw.get("createdAt"),
        "verified_purchase": raw.get("verifiedPurchase") or raw.get("verified_purchase"),
        "helpful_votes": raw.get("helpfulVotes") or raw.get("helpful_votes"),
        "source": "Canopy product/reviews",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    AMZ.mkdir(parents=True, exist_ok=True)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    requests_used = 0
    new_reviews: List[Dict[str, Any]] = []
    product_summaries: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    plan = []

    if not API_KEYS:
        plan = [{**item, "planned_action": "dry_run_no_key_no_canopy_request"} for item in ASINS]
    else:
        for item in ASINS:
            asin_state = state.setdefault("asins", {}).setdefault(item["asin"], {"seen_review_keys": []})
            seen = set(asin_state.get("seen_review_keys", []))

            # P1 sound-machine variants: product summary only by default; do not spend reviews on every variant.
            if item["mode"] == "product_then_maybe_reviews":
                if requests_used >= MAX_REQUESTS:
                    break
                try:
                    payload = canopy_get("product", {"asin": item["asin"], "domain": DOMAIN})
                    requests_used += 1
                    summary = {**item, **extract_product(payload), "checked_at": datetime.now(timezone.utc).isoformat()}
                    product_summaries.append(summary)
                    asin_state["last_product_checked_at"] = summary["checked_at"]
                except Exception as e:
                    errors.append({"asin": item["asin"], "model": item["model"], "stage": "product", "error": str(e)[:240]})
                continue

            page = 1
            while requests_used < MAX_REQUESTS:
                try:
                    payload = canopy_get("product/reviews", {"asin": item["asin"], "domain": DOMAIN, "page": page})
                    requests_used += 1
                    reviews, page_info = extract_reviews(payload)
                    if not reviews:
                        break
                    page_new = []
                    hit_seen = False
                    for raw in reviews:
                        key = review_key(raw, item["asin"])
                        if key in seen:
                            hit_seen = True
                            continue
                        nr = normalize_review(raw, item)
                        page_new.append(nr)
                        seen.add(key)
                    new_reviews.extend(page_new)
                    asin_state["seen_review_keys"] = list(seen)[-1000:]
                    asin_state["last_reviews_checked_at"] = datetime.now(timezone.utc).isoformat()
                    if page_new:
                        asin_state["last_new_review_at"] = asin_state["last_reviews_checked_at"]
                    if hit_seen or not page_info.get("hasNextPage"):
                        break
                    # Keep first run bounded: max 2 pages per ASIN, total budget still dominates.
                    if page >= int(os.getenv("AMAZON_CANOPY_MAX_PAGES_PER_ASIN", "2")):
                        break
                    page += 1
                except Exception as e:
                    errors.append({"asin": item["asin"], "model": item["model"], "stage": "reviews", "error": str(e)[:240]})
                    break

    run = {
        "date": TODAY,
        "domain": DOMAIN,
        "max_requests": MAX_REQUESTS,
        "requests_used": requests_used,
        "new_review_count": len(new_reviews),
        "product_summary_count": len(product_summaries),
        "errors": errors,
        "unlisted": UNLISTED,
        "dry_run": not bool(API_KEYS),
        "canopy_key_count": len(API_KEYS),
    }
    state.setdefault("runs", []).append(run)
    state["runs"] = state["runs"][-30:]
    save_state(state)

    (OUTDIR / "new_reviews.json").write_text(json.dumps(new_reviews, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTDIR / "product_summaries.json").write_text(json.dumps(product_summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTDIR / "summary.json").write_text(json.dumps({**run, "plan": plan}, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# Momcozy Amazon 增量采集｜{TODAY}",
        "",
        f"- Canopy 请求预算：{MAX_REQUESTS}",
        f"- 实际请求数：{requests_used}",
        f"- 新增评论数：{len(new_reviews)}",
        f"- 商品摘要数：{len(product_summaries)}",
        f"- Dry run：{'是（未检测到 CANOPY_API_KEYS/CANOPY_API_KEY）' if not API_KEYS else '否'}",
        "",
        "## 新策略",
        "- 固定 ASIN 白名单，不用 Canopy 做搜索。",
        "- P0 每个 ASIN 默认只抓第一页；第一页无新增即停止。",
        "- Baby Sound Machine 多 ASIN 先做商品摘要，不默认全量 reviews。",
        "- M10、BM04M/BM05 暂未上架，不消耗 reviews 配额。",
    ]
    if errors:
        md += ["", "## 错误", *[f"- {e['model']} {e['asin']} {e['stage']}: {e['error']}" for e in errors]]
    (OUTDIR / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(run, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
