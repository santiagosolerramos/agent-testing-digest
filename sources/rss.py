import feedparser
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

from config import LOOKBACK_DAYS, MAX_ITEMS_PER_SOURCE, RSS_FEEDS
from sources.base import SourceItem


def fetch() -> list[SourceItem]:
    items: list[SourceItem] = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    for feed_name, feed_url in RSS_FEEDS:
        entries = _fetch_feed(feed_name, feed_url, cutoff)
        items.extend(entries)

    return items[:MAX_ITEMS_PER_SOURCE]


def _fetch_feed(name: str, url: str, cutoff: datetime) -> list[SourceItem]:
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"[rss] Error parsing feed '{name}': {e}")
        return []

    items = []
    for entry in feed.entries:
        date = _parse_date(entry)
        if date is None or date < cutoff:
            continue

        title = entry.get("title", "").strip()
        link = entry.get("link", "")
        summary = _extract_summary(entry)

        if not title or not link:
            continue

        items.append(
            SourceItem(
                title=title,
                url=link,
                summary=summary,
                date=date,
                source="rss",
                extra={"feed": name},
            )
        )

    return items


def _parse_date(entry) -> datetime | None:
    for field in ("published", "updated"):
        raw = entry.get(field)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(raw)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc)

    return None


def _extract_summary(entry) -> str:
    for field in ("summary", "description", "content"):
        value = entry.get(field)
        if not value:
            continue
        if isinstance(value, list):
            value = value[0].get("value", "")
        # Strip HTML tags naively
        import re
        text = re.sub(r"<[^>]+>", " ", value)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:400]
    return ""
