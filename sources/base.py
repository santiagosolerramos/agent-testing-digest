from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SourceItem:
    title: str
    url: str
    summary: str
    date: datetime
    source: str                    # e.g. "arxiv", "hackernews", "github", "rss"
    score: int = 0                 # filled in by ranker
    extra: dict = field(default_factory=dict)  # source-specific metadata

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return isinstance(other, SourceItem) and self.url == other.url
