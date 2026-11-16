"""
Google SERP fetcher using SerpApi.

Two public functions:
  - parse_organic_results(raw: dict) -> list[SerpItem]
      Pure function: takes raw SerpApi JSON dict, returns only organic results.
      No network calls → 100% unit-testable with fixture data.

  - search(query: str, api_key: str, **kwargs) -> list[SerpItem]
      Makes real SerpApi request and returns parsed organic results.
"""
import serpapi
from app.scraper.models import SerpItem


def parse_organic_results(raw: dict) -> list[SerpItem]:
    """
    Parse SerpApi response dict and return only organic (natural) results.

    SerpApi clearly separates organic_results from ads (ads_results),
    shopping results, knowledge panel etc. — so we simply use the
    'organic_results' key and ignore everything else.

    Args:
        raw: Raw JSON dict returned by SerpApi (or loaded from fixture).

    Returns:
        List of SerpItem, one per organic result, ordered by position.
    """
    organic = raw.get("organic_results", [])
    results: list[SerpItem] = []

    for item in organic:
        rank = item.get("position", len(results) + 1)
        title = item.get("title", "")
        url = item.get("link", "")
        displayed_url = item.get("displayed_link", "")
        snippet = item.get("snippet", "")

        # Skip items without a URL or title (occasionally SerpApi returns
        # partial entries for things like sitelinks headers)
        if not url or not title:
            continue

        results.append(SerpItem(
            rank=rank,
            title=title,
            url=url,
            displayed_url=displayed_url,
            snippet=snippet,
        ))

    return results


def search(query: str, api_key: str, hl: str = "cs", gl: str = "cz", num: int = 10) -> list[SerpItem]:
    """
    Fetch organic Google search results for query via SerpApi.

    Args:
        query:   Search keyword / phrase.
        api_key: SerpApi private API key.
        hl:      Language code (default: 'cs' for Czech).
        gl:      Country code (default: 'cz' for Czech Republic).
        num:     Number of results to request (default: 10).

    Returns:
        List of SerpItem representing organic results.

    Raises:
        Exception: Propagates SerpApi errors (invalid key, quota exceeded, etc.)
    """
    client = serpapi.Client(api_key=api_key)
    raw = client.search({
        "engine": "google",
        "q": query,
        "hl": hl,
        "gl": gl,
        "num": num,
    })
    return parse_organic_results(dict(raw))
