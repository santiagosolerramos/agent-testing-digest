from datetime import datetime, timezone, timedelta

from config import LOOKBACK_DAYS, MAX_ITEMS_PER_SOURCE, TAVILY_API_KEY
from sources.base import SourceItem

QUERIES = [
    "AI agent evaluation framework 2026",
    "LLM testing synthetic users",
    "conversational agent testing",
    "agent regression testing",
    "WhatsApp AI agent evaluation",
    # Competitor intelligence
    "Sierra AI agent blog",
    "Wonderful AI agents blog",
    "Decagon AI blog",
    "Intercom AI agent",
    "Forethought AI",
    "Parloa AI",
    "Cognigy AI agent blog",
    "Yellow.ai conversational agent",
    "MavenAGI customer support",
    "PolyAI conversational AI",
    "Retell AI voice agent",
    "Kustomer AI agent",
]

# Tavily will prioritize results from these domains when used in include_domains
COMPETITOR_DOMAINS = [
    "sierra.ai",
    "wonderful.ai",
    "decagon.com",
    "intercom.com",
    "cognigy.com",
    "yellow.ai",
    "mavenagi.com",
    "kustomer.com",
    "poly.ai",
    "retellai.com",
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

    for query in QUERIES:
        results = _search(client, query, cutoff)
        for item in results:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                items.append(item)

    return items[:MAX_ITEMS_PER_SOURCE]


def _search(client, query: str, cutoff: datetime) -> list[SourceItem]:
    is_competitor_query = any(
        domain.split(".")[0] in query.lower() for domain in COMPETITOR_DOMAINS
    )
    kwargs = {
        "query": query,
        "search_depth": "advanced",
        "max_results": 5,
    }
    if is_competitor_query:
        kwargs["include_domains"] = COMPETITOR_DOMAINS

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
