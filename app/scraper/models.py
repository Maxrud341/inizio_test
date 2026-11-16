from dataclasses import dataclass, asdict


@dataclass
class SerpItem:
    """Represents a single organic search result from Google SERP."""
    rank: int
    title: str
    url: str
    displayed_url: str
    snippet: str

    def to_dict(self) -> dict:
        return asdict(self)
