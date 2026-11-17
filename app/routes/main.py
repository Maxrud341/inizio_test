"""
Main blueprint — all application routes.

GET  /              → Render search page (index.html)
POST /api/search    → Run search, return JSON list of organic results
POST /api/export    → Return downloadable file (json or csv)
"""
import csv
import io
import json

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    Response,
)

from app.scraper.google_serp import search
from app.scraper.models import SerpItem

main_bp = Blueprint("main", __name__)


# ------------------------------------------------------------------ #
#  GET /  — search page                                               #
# ------------------------------------------------------------------ #
@main_bp.get("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------------------ #
#  POST /api/search  — perform search, return JSON                    #
# ------------------------------------------------------------------ #
@main_bp.post("/api/search")
def api_search():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    api_key = current_app.config.get("SERPAPI_KEY", "")
    if not api_key:
        return jsonify({"error": "SERPAPI_KEY is not configured"}), 500

    try:
        results: list[SerpItem] = search(
            query=query,
            api_key=api_key,
            hl=current_app.config["SEARCH_HL"],
            gl=current_app.config["SEARCH_GL"],
            google_domain=current_app.config.get("SEARCH_GOOGLE_DOMAIN", "google.cz"),
            location=current_app.config.get("SEARCH_LOCATION", "Czechia"),
            num=current_app.config["SEARCH_NUM"],
        )
    except Exception as exc:
        current_app.logger.error("SerpApi error: %s", exc)
        return jsonify({"error": str(exc)}), 502

    return jsonify({
        "query": query,
        "count": len(results),
        "results": [r.to_dict() for r in results],
    })


# ------------------------------------------------------------------ #
#  POST /api/export  — download results as JSON or CSV               #
# ------------------------------------------------------------------ #
@main_bp.post("/api/export")
def api_export():
    data = request.get_json(silent=True) or {}
    fmt = (data.get("format") or "json").lower()
    results_raw = data.get("results", [])
    query = (data.get("query") or "search").strip()

    if fmt not in ("json", "csv"):
        return jsonify({"error": "Format must be 'json' or 'csv'"}), 400

    if not results_raw:
        return jsonify({"error": "No results provided"}), 400

    safe_query = "".join(c if c.isalnum() or c in "-_ " else "_" for c in query)[:40].strip()
    filename = f"serp_{safe_query}.{fmt}"

    if fmt == "json":
        payload = json.dumps(
            {"query": query, "results": results_raw},
            ensure_ascii=False,
            indent=2,
        )
        return Response(
            payload,
            mimetype="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # --- CSV ---
    output = io.StringIO()
    # UTF-8 BOM so Excel opens it correctly
    output.write("\ufeff")
    fieldnames = ["rank", "title", "url", "displayed_url", "snippet"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(results_raw)

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
