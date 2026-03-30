#!/usr/bin/env python3
"""
agent-testing-digest
Daily research digest on agent evaluation & LLM testing for Connectly.

Usage:
    python main.py                 # Run for today
    python main.py --date 2024-01-15  # Run for a specific date (fetch window unchanged)
    python main.py --no-mark-seen  # Don't persist seen URLs (useful for testing)
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from config import REPORTS_DIR, XAI_API_KEY, GITHUB_TOKEN, LOOKBACK_DAYS, MIN_SCORE, MAX_ITEMS_PER_SOURCE
from sources import fetch_all
from ranker import rank_and_filter, mark_seen, score_debug
from renderer import render

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "this", "that", "these",
    "those", "it", "its", "we", "our", "you", "your", "they", "their",
    "not", "no", "can", "all", "more", "new", "using", "based", "via",
}


def main():
    args = _parse_args()
    run_date = args.date or date.today()

    print(f"\n=== agent-testing-digest | {run_date.isoformat()} ===\n")

    # DEBUG: confirm .env loaded correctly — remove once verified
    print("[debug] XAI_API_KEY:", XAI_API_KEY[:8] + "..." if XAI_API_KEY else "NOT SET")
    print("[debug] GITHUB_TOKEN:", GITHUB_TOKEN[:8] + "..." if GITHUB_TOKEN and not GITHUB_TOKEN.startswith("ghp_...") else GITHUB_TOKEN or "NOT SET")
    print(f"[debug] LOOKBACK_DAYS={LOOKBACK_DAYS}  MIN_SCORE={MIN_SCORE}  MAX_ITEMS_PER_SOURCE={MAX_ITEMS_PER_SOURCE}\n")

    # 1. Fetch
    print("Fetching from all sources...")
    raw_items = fetch_all()
    print(f"Total raw items: {len(raw_items)}\n")

    # 2. Debug dump (before ranking, scores all items regardless of MIN_SCORE/seen)
    if args.debug:
        _write_debug(raw_items, run_date)

    # 3. Rank & filter
    print("Ranking and filtering...")
    ranked = rank_and_filter(raw_items)
    print(f"Items after ranking (score >= {_min_score()}): {len(ranked)}\n")

    if not ranked:
        print("No relevant items found. Try lowering MIN_SCORE or increasing LOOKBACK_DAYS.")

    # 4. Render
    print("Generating digest with Grok...")
    digest = render(ranked, run_date)

    # 5. Write report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"digest_{run_date.isoformat()}.md"
    report_path.write_text(digest, encoding="utf-8")
    print(f"\nDigest written to: {report_path}")

    # 6. Persist seen URLs
    if not args.no_mark_seen and ranked:
        mark_seen(ranked)
        print(f"Marked {len(ranked)} URLs as seen.\n")

    print(digest)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily agent eval digest")
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=None,
        help="Report date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--no-mark-seen",
        action="store_true",
        help="Skip persisting seen URLs (useful for re-running without skipping items)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save all raw items with keyword matches to reports/debug_YYYY-MM-DD.json",
    )
    return parser.parse_args()


def _write_debug(raw_items, run_date: date) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    debug_path = REPORTS_DIR / f"debug_{run_date.isoformat()}.json"

    records = []
    for item in raw_items:
        item_score, matched_keywords = score_debug(item)
        record = {
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "summary": item.summary,
            "score": item_score,
            "matched_keywords": matched_keywords,
        }
        if item_score == 0:
            text = f"{item.title} {item.summary}"
            words = re.findall(r"[a-z]{3,}", text.lower())
            counts = Counter(w for w in words if w not in _STOPWORDS)
            record["suggested_keywords"] = [w for w, _ in counts.most_common(10)]
        records.append(record)

    records.sort(key=lambda r: r["score"], reverse=True)
    debug_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Debug dump written to: {debug_path} ({len(records)} items)\n")


def _min_score() -> int:
    from config import MIN_SCORE
    return MIN_SCORE


if __name__ == "__main__":
    main()
