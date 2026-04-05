import json
from pathlib import Path

from config import HIGH_VALUE_KEYWORDS, MEDIUM_VALUE_KEYWORDS, MIN_SCORE, SEEN_URLS_FILE
from sources.base import SourceItem

COMPETITOR_DOMAINS = [
    "sierra.ai",
    "wonderful.ai",
    "decagon.com",
    "intercom.com",
    "forethought.ai",
    "parloa.com",
    "brainlid.org",
    "hamming.ai",
    "braintrust.dev",
    "humanloop.com",
    "cognigy.com",
    "yellow.ai",
    "mavenagi.com",
    "kustomer.com",
    "poly.ai",
    "retellai.com",
    "moveworks.com",
    "kore.ai",
]


def rank_and_filter(items: list[SourceItem]) -> list[SourceItem]:
    """Score items by relevance, filter by MIN_SCORE, remove already-seen URLs."""
    seen = _load_seen_urls()

    scored = []
    for item in items:
        if item.url in seen:
            continue
        item.score = _score(item)
        if item.score >= MIN_SCORE:
            scored.append(item)

    scored.sort(key=lambda x: (x.score, x.date), reverse=True)
    return scored


def mark_seen(items: list[SourceItem]) -> None:
    """Persist URLs so they are skipped in future runs."""
    seen = _load_seen_urls()
    seen.update(item.url for item in items)
    SEEN_URLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_URLS_FILE.write_text(json.dumps(list(seen), indent=2))


def score_debug(item: SourceItem) -> tuple[int, list[str]]:
    """Score an item and return (score, matched_keywords). Used for --debug output."""
    text = f"{item.title} {item.summary}".lower()
    score = 0
    matched: list[str] = []

    for kw in HIGH_VALUE_KEYWORDS:
        if kw.lower() in text:
            score += 2
            matched.append(kw)

    for kw in MEDIUM_VALUE_KEYWORDS:
        if kw.lower() in text:
            score += 1
            matched.append(kw)

    if item.source == "arxiv":
        score += 1
    if item.source == "hackernews" and item.extra.get("points", 0) > 50:
        score += 1
    if item.source == "github":
        score += 1
    if any(domain in item.url for domain in COMPETITOR_DOMAINS):
        score += 3
        matched.append(f"competitor domain")

    return score, matched


def _score(item: SourceItem) -> int:
    text = f"{item.title} {item.summary}".lower()
    score = 0

    for kw in HIGH_VALUE_KEYWORDS:
        if kw.lower() in text:
            score += 2

    for kw in MEDIUM_VALUE_KEYWORDS:
        if kw.lower() in text:
            score += 1

    # Source-specific bonuses
    if item.source == "arxiv":
        score += 1  # Papers are generally high-signal
    if item.source == "hackernews" and item.extra.get("points", 0) > 50:
        score += 1
    if item.source == "github":
        score += 1  # Releases from monitored repos are always relevant
    if any(domain in item.url for domain in COMPETITOR_DOMAINS):
        score += 3  # Competitor content always surfaces above MIN_SCORE

    return score


def _load_seen_urls() -> set[str]:
    if not Path(SEEN_URLS_FILE).exists():
        return set()
    try:
        data = json.loads(Path(SEEN_URLS_FILE).read_text())
        return set(data)
    except (json.JSONDecodeError, TypeError):
        return set()
