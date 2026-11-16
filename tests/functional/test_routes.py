"""
Functional tests for Flask routes.

These tests use Flask's built-in test client — no real server needed.
SerpApi calls are mocked so tests are offline, fast and deterministic.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from app import create_app
from app.scraper.models import SerpItem

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_serp.json"

MOCK_RESULTS = [
    SerpItem(rank=1, title="Collabim SEO", url="https://www.collabim.cz",
             displayed_url="www.collabim.cz", snippet="Nejlepší SEO nástroj."),
    SerpItem(rank=2, title="Semrush", url="https://cs.semrush.com",
             displayed_url="cs.semrush.com", snippet="Komplexní SEO platforma."),
]


@pytest.fixture
def app():
    app = create_app("development")
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# ------------------------------------------------------------------ #
#  GET /                                                              #
# ------------------------------------------------------------------ #
class TestIndexRoute:
    def test_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_returns_html(self, client):
        r = client.get("/")
        assert b"html" in r.data.lower()


# ------------------------------------------------------------------ #
#  POST /api/search                                                   #
# ------------------------------------------------------------------ #
class TestSearchRoute:
    def test_empty_query_returns_400(self, client):
        r = client.post("/api/search", json={"query": ""})
        assert r.status_code == 400
        assert "error" in r.get_json()

    def test_missing_query_returns_400(self, client):
        r = client.post("/api/search", json={})
        assert r.status_code == 400

    @patch("app.routes.main.search", return_value=MOCK_RESULTS)
    def test_valid_query_returns_200(self, mock_search, client):
        r = client.post("/api/search", json={"query": "seo nastroje"})
        assert r.status_code == 200

    @patch("app.routes.main.search", return_value=MOCK_RESULTS)
    def test_response_contains_results_key(self, mock_search, client):
        r = client.post("/api/search", json={"query": "seo nastroje"})
        data = r.get_json()
        assert "results" in data
        assert "query" in data
        assert "count" in data

    @patch("app.routes.main.search", return_value=MOCK_RESULTS)
    def test_result_count_matches(self, mock_search, client):
        r = client.post("/api/search", json={"query": "seo nastroje"})
        data = r.get_json()
        assert data["count"] == 2
        assert len(data["results"]) == 2

    @patch("app.routes.main.search", return_value=MOCK_RESULTS)
    def test_result_has_required_fields(self, mock_search, client):
        r = client.post("/api/search", json={"query": "seo nastroje"})
        result = r.get_json()["results"][0]
        for field in ("rank", "title", "url", "snippet", "displayed_url"):
            assert field in result, f"Missing field: {field}"

    @patch("app.routes.main.search", return_value=MOCK_RESULTS)
    def test_no_ad_urls_in_response(self, mock_search, client):
        """Ensure the API never returns ad/tracking URLs."""
        r = client.post("/api/search", json={"query": "seo nastroje"})
        for item in r.get_json()["results"]:
            assert "googleadservices" not in item["url"]

    @patch("app.routes.main.search", side_effect=Exception("SerpApi quota exceeded"))
    def test_serpapi_error_returns_502(self, mock_search, client):
        r = client.post("/api/search", json={"query": "seo nastroje"})
        assert r.status_code == 502
        assert "error" in r.get_json()


# ------------------------------------------------------------------ #
#  POST /api/export                                                   #
# ------------------------------------------------------------------ #
class TestExportRoute:
    @pytest.fixture
    def results_payload(self):
        return [r.to_dict() for r in MOCK_RESULTS]

    def test_json_export_returns_200(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo nastroje", "format": "json", "results": results_payload
        })
        assert r.status_code == 200

    def test_json_export_content_type(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo", "format": "json", "results": results_payload
        })
        assert "application/json" in r.content_type

    def test_json_export_is_attachment(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo", "format": "json", "results": results_payload
        })
        assert "attachment" in r.headers["Content-Disposition"]
        assert ".json" in r.headers["Content-Disposition"]

    def test_json_export_body_is_valid_json(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo", "format": "json", "results": results_payload
        })
        parsed = json.loads(r.data)
        assert "results" in parsed
        assert len(parsed["results"]) == 2

    def test_csv_export_returns_200(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo nastroje", "format": "csv", "results": results_payload
        })
        assert r.status_code == 200

    def test_csv_export_content_type(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo", "format": "csv", "results": results_payload
        })
        assert "text/csv" in r.content_type

    def test_csv_export_has_header_row(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo", "format": "csv", "results": results_payload
        })
        # Strip UTF-8 BOM before checking
        text = r.data.decode("utf-8-sig")
        first_line = text.splitlines()[0]
        assert "rank" in first_line
        assert "title" in first_line
        assert "url" in first_line

    def test_csv_export_row_count(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo", "format": "csv", "results": results_payload
        })
        text = r.data.decode("utf-8-sig")
        rows = [l for l in text.splitlines() if l.strip()]
        # 1 header + 2 data rows
        assert len(rows) == 3

    def test_invalid_format_returns_400(self, client, results_payload):
        r = client.post("/api/export", json={
            "query": "seo", "format": "xml", "results": results_payload
        })
        assert r.status_code == 400

    def test_empty_results_returns_400(self, client):
        r = client.post("/api/export", json={
            "query": "seo", "format": "json", "results": []
        })
        assert r.status_code == 400
