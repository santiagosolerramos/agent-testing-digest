from datetime import datetime, timezone, timedelta

from config import LOOKBACK_DAYS, MAX_ITEMS_PER_SOURCE, TAVILY_API_KEY
from sources.base import SourceItem

GENERAL_QUERIES = [
    "AI agent evaluation framework 2026",
    "LLM testing synthetic users",
    "conversational agent testing",
    "agent regression testing",
    "WhatsApp AI agent evaluation",
]

# (query, domain) — Tavily will restrict results to that domain
COMPETITOR_QUERIES: list[tuple[str, str]] = [
    ("Sierra AI agent evaluation 2026", "sierra.ai"),
    ("Wonderful AI agent release 2026", "wonderful.ai"),
    ("Decagon AI engineering blog 2026", "decagon.com"),
    ("Intercom AI agent feature update 2026", "intercom.com"),
    ("Forethought AI support automation 2026", "forethought.ai"),
    ("Parloa voice AI agent 2026", "parloa.com"),
    ("Cognigy AI agent evaluation 2026", "cognigy.com"),
    ("Yellow.ai conversational AI update 2026", "yellow.ai"),
    ("MavenAGI customer support AI 2026", "mavenagi.com"),
    ("PolyAI voice agent release 2026", "poly.ai"),
    ("Retell AI voice agent update 2026", "retellai.com"),
    ("Kustomer AI agent automation 2026", "kustomer.com"),
]


def fetch() -> list[SourceItem]:
    if not TAVILY_API_KEY:
        print("[web_search] TAVILY_API_KEY not set, skipping")
        return []

    from tavily import TavilyClient
    client = TavilyClient(api_key=TAVILY_API_KEY)
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    items: list[SourceItem] = []
    seen_urls: set[str] = set()

    for query in GENERAL_QUERIES:
        results = _search(client, query, cutoff)
        for item in results:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                items.append(item)

    for query, domain in COMPETITOR_QUERIES:
        results = _search(client, query, cutoff, include_domain=domain)
        for item in results:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                items.append(item)

    return items[:MAX_ITEMS_PER_SOURCE]


def _search(client, query: str, cutoff: datetime, include_domain: str | None = None) -> list[SourceItem]:
    kwargs = {
        "query": query,
        "search_depth": "advanced",
        "max_results": 5,
    }
    if include_domain:
        kwargs["include_domains"] = [include_domain]

    try:
        response = client.search(**kwargs)
    except Exception as e:
        print(f"[web_search] error for query '{query}': {e}")
        return []

    items = []
    for result in response.get("results", []):
        url = result.get("url", "")
        title = result.get("title", "").strip()
        if not url or not title:
            continue

        # Tavily doesn't always return a published date — use today as fallback
        raw_date = result.get("published_date")
        if raw_date:
            try:
                date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
            except ValueError:
                date = datetime.now(timezone.utc)
        else:
            date = datetime.now(timezone.utc)

        if date < cutoff:
            continue

        summary = (result.get("content") or "").strip()[:400]

        items.append(
            SourceItem(
                title=title,
                url=url,
                summary=summary,
                date=date,
                source="tavily",
                extra={"query": query, "score": result.get("score", 0)},
            )
        )

    return items
