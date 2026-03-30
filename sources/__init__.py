from sources import arxiv, hackernews, github_releases, rss
from sources.base import SourceItem


def fetch_all() -> list[SourceItem]:
    """Run all sources and return a combined, deduplicated list of items."""
    all_items: list[SourceItem] = []
    seen_urls: set[str] = set()

    sources = [
        ("arxiv", arxiv.fetch),
        ("hackernews", hackernews.fetch),
        ("github", github_releases.fetch),
        ("rss", rss.fetch),
    ]

    for name, fetch_fn in sources:
        try:
            items = fetch_fn()
            print(f"[{name}] fetched {len(items)} items")
        except Exception as e:
            print(f"[{name}] failed: {e}")
            items = []

        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                all_items.append(item)

    return all_items
