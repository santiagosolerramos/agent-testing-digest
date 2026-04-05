import httpx
from datetime import datetime, timezone, timedelta

from config import LOOKBACK_DAYS, MAX_ITEMS_PER_SOURCE
from sources.base import SourceItem

ALGOLIA_API = "https://hn.algolia.com/api/v1/search"

QUERIES = [
    "agent evaluation",
    "LLM evals",
    "agent testing",
    "synthetic user",
    "conversational AI testing",
    "LLM benchmark",
    "llm testing",
    "synthetic user simulation",
]


def fetch() -> list[SourceItem]:
    items: list[SourceItem] = []
    seen_ids: set[str] = set()
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).timestamp())

    for query in QUERIES:
        results = _search(query, cutoff_ts)
        for item in results:
            if item.url not in seen_ids:
                seen_ids.add(item.url)
                items.append(item)

    return items[:MAX_ITEMS_PER_SOURCE]


def _search(query: str, cutoff_ts: int) -> list[SourceItem]:
    params = {
        "query": query,
        "tags": "(story,ask_hn)",
        "numericFilters": f"created_at_i>{cutoff_ts},points>5",
        "hitsPerPage": 20,
    }
    try:
        response = httpx.get(ALGOLIA_API, params=params, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[hackernews] HTTP error for query '{query}': {e}")
        return []

    data = response.json()
    items = []

    for hit in data.get("hits", []):
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        title = hit.get("title", "").strip()
        if not title:
            continue

        created_at = hit.get("created_at")
        date = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else datetime.now(timezone.utc)

        items.append(
            SourceItem(
                title=title,
                url=url,
                summary=f"HN discussion — {hit.get('num_comments', 0)} comments, {hit.get('points', 0)} points.",
                date=date,
                source="hackernews",
                extra={
                    "points": hit.get("points", 0),
                    "num_comments": hit.get("num_comments", 0),
                    "hn_url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                },
            )
        )

    return items
