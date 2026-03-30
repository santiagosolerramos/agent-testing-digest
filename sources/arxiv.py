import httpx
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

from config import LOOKBACK_DAYS, MAX_ITEMS_PER_SOURCE
from sources.base import SourceItem

ARXIV_API = "https://export.arxiv.org/api/query"

QUERIES = [
    "agent evaluation",
    "LLM evaluation framework",
    "synthetic user simulation",
    "conversational agent testing",
    "LLM regression testing",
    "multi-turn dialogue evaluation",
]


def fetch() -> list[SourceItem]:
    items: list[SourceItem] = []
    seen_ids: set[str] = set()
    cutoff = _cutoff_date()

    for query in QUERIES:
        results = _search(query, max_results=MAX_ITEMS_PER_SOURCE)
        for item in results:
            if item.url not in seen_ids and item.date >= cutoff:
                seen_ids.add(item.url)
                items.append(item)

    return items


def _search(query: str, max_results: int) -> list[SourceItem]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    try:
        response = httpx.get(ARXIV_API, params=params, timeout=20)
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[arxiv] HTTP error for query '{query}': {e}")
        return []

    return _parse(response.text)


def _parse(xml_text: str) -> list[SourceItem]:
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(xml_text)
    items = []

    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)
        id_el = entry.find("atom:id", ns)

        if not all([title_el, summary_el, published_el, id_el]):
            continue

        title = (title_el.text or "").strip().replace("\n", " ")
        summary = (summary_el.text or "").strip().replace("\n", " ")[:500]
        url = (id_el.text or "").strip()
        date = datetime.fromisoformat(
            (published_el.text or "").replace("Z", "+00:00")
        )

        authors = [
            a.find("atom:name", ns).text
            for a in entry.findall("atom:author", ns)
            if a.find("atom:name", ns) is not None
        ]

        items.append(
            SourceItem(
                title=title,
                url=url,
                summary=summary,
                date=date,
                source="arxiv",
                extra={"authors": authors},
            )
        )

    return items


def _cutoff_date() -> datetime:
    from datetime import timedelta
    return datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
