import httpx
from datetime import datetime, timezone, timedelta

from config import LOOKBACK_DAYS, MAX_ITEMS_PER_SOURCE, GITHUB_TOKEN, GITHUB_REPOS
from sources.base import SourceItem

GITHUB_API = "https://api.github.com"


def fetch() -> list[SourceItem]:
    items: list[SourceItem] = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    headers = _build_headers()

    for repo in GITHUB_REPOS:
        releases = _fetch_releases(repo, headers, cutoff)
        items.extend(releases)

    return items[:MAX_ITEMS_PER_SOURCE]


def _fetch_releases(repo: str, headers: dict, cutoff: datetime) -> list[SourceItem]:
    url = f"{GITHUB_API}/repos/{repo}/releases"
    try:
        response = httpx.get(url, headers=headers, params={"per_page": 10}, timeout=15, follow_redirects=True)
        if response.status_code == 404:
            return []
        response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[github] HTTP error for {repo}: {e}")
        return []

    items = []
    for release in response.json():
        published = release.get("published_at")
        if not published:
            continue

        date = datetime.fromisoformat(published.replace("Z", "+00:00"))
        if date < cutoff:
            continue

        tag = release.get("tag_name", "")
        name = release.get("name") or tag
        body = (release.get("body") or "").strip()[:400]

        items.append(
            SourceItem(
                title=f"{repo} {name}",
                url=release.get("html_url", ""),
                summary=body or f"New release {tag} published.",
                date=date,
                source="github",
                extra={"repo": repo, "tag": tag},
            )
        )

    return items


def _build_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN.strip()}"
    return headers
