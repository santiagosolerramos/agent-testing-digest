from datetime import date

from openai import OpenAI

from config import XAI_API_KEY, XAI_BASE_URL, XAI_MODEL, PROMPTS_DIR
from sources.base import SourceItem

_client = OpenAI(api_key=XAI_API_KEY, base_url=XAI_BASE_URL)


def render(items: list[SourceItem], run_date: date) -> str:
    """Call Grok to generate the Markdown digest and return it as a string."""
    if not items:
        return _empty_digest(run_date)

    system_prompt = _load_system_prompt()
    user_message = _build_user_message(items, run_date)

    response = _client.chat.completions.create(
        model=XAI_MODEL,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content


def _load_system_prompt() -> str:
    path = PROMPTS_DIR / "digest.md"
    return path.read_text(encoding="utf-8")


def _build_user_message(items: list[SourceItem], run_date: date) -> str:
    lines = [
        f"Today's date: {run_date.isoformat()}",
        f"Total items to process: {len(items)}",
        "",
        "Please generate the digest for the following research items:",
        "",
    ]

    for i, item in enumerate(items, 1):
        lines.append(f"## Item {i}")
        lines.append(f"**Title:** {item.title}")
        lines.append(f"**URL:** {item.url}")
        lines.append(f"**Source:** {item.source}")
        lines.append(f"**Date:** {item.date.strftime('%Y-%m-%d')}")
        lines.append(f"**Relevance score:** {item.score}")

        if item.source == "arxiv" and item.extra.get("authors"):
            authors = ", ".join(item.extra["authors"][:3])
            if len(item.extra["authors"]) > 3:
                authors += " et al."
            lines.append(f"**Authors:** {authors}")

        if item.source == "hackernews":
            lines.append(
                f"**HN stats:** {item.extra.get('points', 0)} points, "
                f"{item.extra.get('num_comments', 0)} comments"
            )
            lines.append(f"**HN thread:** {item.extra.get('hn_url', '')}")

        if item.source == "github":
            lines.append(f"**Repo:** {item.extra.get('repo', '')}")
            lines.append(f"**Tag:** {item.extra.get('tag', '')}")

        if item.source == "rss":
            lines.append(f"**Feed:** {item.extra.get('feed', '')}")

        lines.append(f"**Summary:** {item.summary}")
        lines.append("")

    return "\n".join(lines)


def _empty_digest(run_date: date) -> str:
    return (
        f"# Agent Eval Digest — {run_date.isoformat()}\n\n"
        "No new relevant items found today. "
        "Try increasing `LOOKBACK_DAYS` or lowering `MIN_SCORE` in your `.env`.\n"
    )
