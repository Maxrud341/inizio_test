"""
Unit tests for parse_organic_results() in app.scraper.google_serp.

These tests are:
  - Offline: no network calls, no API key needed.
  - Fast:    run in < 100ms total.
  - Deterministic: always produce the same result.

The fixture (tests/fixtures/sample_serp.json) is a realistic SerpApi
JSON response that includes organic results AND an ad block, letting us
verify that ads are excluded and only organic results are returned.
"""
import json
import pytest
from pathlib import Path

from app.scraper.google_serp import parse_organic_results
from app.scraper.models import SerpItem


FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_serp.json"


@pytest.fixture
def raw_serp() -> dict:
    """Load the sample SerpApi fixture JSON."""
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def organic_results(raw_serp) -> list[SerpItem]:
    """Parsed organic results from the fixture."""
    return parse_organic_results(raw_serp)


# ------------------------------------------------------------------
# 1. Count & ordering
# ------------------------------------------------------------------

class TestOrganicCount:
    def test_returns_ten_results(self, organic_results):
        """Fixture contains 10 organic results — all should be returned."""
        assert len(organic_results) == 10

    def test_ordered_by_position(self, organic_results):
        """Results must be in ascending order by rank (position)."""
        ranks = [r.rank for r in organic_results]
        assert ranks == sorted(ranks)

    def test_first_rank_is_one(self, organic_results):
        """First organic result must have rank == 1."""
        assert organic_results[0].rank == 1

    def test_last_rank_is_ten(self, organic_results):
        """Last organic result must have rank == 10."""
        assert organic_results[-1].rank == 10


# ------------------------------------------------------------------
# 2. Ads exclusion (critical requirement from the task)
# ------------------------------------------------------------------

class TestAdsExcluded:
    def test_no_ad_urls_in_results(self, organic_results):
        """
        The fixture has 1 ad block (example-ad.cz).
        It must NOT appear in organic results.
        """
        ad_url = "https://www.example-ad.cz/seo-nastroje"
        urls = [r.url for r in organic_results]
        assert ad_url not in urls

    def test_no_googleadservices_urls(self, organic_results):
        """No tracking / ad-serving URLs must appear in results."""
        for r in organic_results:
            assert "googleadservices" not in r.url

    def test_no_ad_snippets(self, organic_results):
        """
        Ad snippets start with 'Reklama:' in Czech locale.
        No such prefix should appear in organic snippets.
        """
        for r in organic_results:
            assert not r.snippet.startswith("Reklama:")


# ------------------------------------------------------------------
# 3. Field completeness
# ------------------------------------------------------------------

class TestFieldCompleteness:
    def test_all_results_have_title(self, organic_results):
        """Every result must have a non-empty title."""
        for r in organic_results:
            assert isinstance(r.title, str) and r.title.strip() != ""

    def test_all_results_have_url(self, organic_results):
        """Every result must have a non-empty URL."""
        for r in organic_results:
            assert isinstance(r.url, str) and r.url.strip() != ""

    def test_all_results_have_snippet(self, organic_results):
        """Every result must have a snippet (may be empty string but not missing)."""
        for r in organic_results:
            assert hasattr(r, "snippet")
            assert isinstance(r.snippet, str)

    def test_all_results_have_rank(self, organic_results):
        """Every result must have a rank that is a positive integer."""
        for r in organic_results:
            assert isinstance(r.rank, int) and r.rank >= 1

    def test_urls_start_with_http(self, organic_results):
        """All result URLs must be absolute HTTP(S) URLs."""
        for r in organic_results:
            assert r.url.startswith("http://") or r.url.startswith("https://")


# ------------------------------------------------------------------
# 4. SerpItem.to_dict() — required for JSON / CSV export
# ------------------------------------------------------------------

class TestSerpItemToDict:
    def test_to_dict_has_all_keys(self, organic_results):
        """to_dict() must include rank, title, url, displayed_url, snippet."""
        expected_keys = {"rank", "title", "url", "displayed_url", "snippet"}
        d = organic_results[0].to_dict()
        assert expected_keys == set(d.keys())

    def test_to_dict_values_match(self, organic_results):
        """to_dict() values must match the original SerpItem attributes."""
        item = organic_results[0]
        d = item.to_dict()
        assert d["rank"] == item.rank
        assert d["title"] == item.title
        assert d["url"] == item.url
        assert d["snippet"] == item.snippet


# ------------------------------------------------------------------
# 5. Edge cases
# ------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_organic_results(self):
        """When SerpApi returns no organic_results, return empty list."""
        result = parse_organic_results({"organic_results": []})
        assert result == []

    def test_missing_organic_results_key(self):
        """When 'organic_results' key is absent, return empty list."""
        result = parse_organic_results({})
        assert result == []

    def test_items_without_url_are_skipped(self):
        """Partial entries (no URL) must be silently skipped."""
        raw = {
            "organic_results": [
                {"position": 1, "title": "Valid", "link": "https://example.com", "snippet": "ok", "displayed_link": "example.com"},
                {"position": 2, "title": "No URL", "link": "", "snippet": "skip", "displayed_link": ""},
                {"position": 3, "title": "", "link": "https://example.com/no-title", "snippet": "skip", "displayed_link": ""},
            ]
        }
        results = parse_organic_results(raw)
        assert len(results) == 1
        assert results[0].url == "https://example.com"

    def test_first_result_is_collabim(self, organic_results):
        """
        Specific check: first result in fixture is Collabim —
        the SEO tool made by INIZIO (the company that issued this task).
        """
        assert "collabim" in organic_results[0].url.lower()
