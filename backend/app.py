"""Google Places Scraper - Flask API"""

import os
from datetime import date, datetime

from dotenv import load_dotenv
from email_scraper import scrape_emails_from_websites
from flask import Flask, jsonify, request
from flask_cors import CORS
from scraper import search_places

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# In-memory job storage
jobs = {}
job_counter = 0


@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "API is running", "version": "1.0.0"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route("/debug-env", methods=["GET"])
def debug_env():
    return jsonify(
        {
            "api_key_set": bool(API_KEY),
            "api_key_length": len(API_KEY) if API_KEY else 0,
        }
    )


@app.route("/test-api", methods=["GET"])
def test_api():
    from scraper import search_places

    try:
        if not API_KEY:
            return jsonify({"status": "error", "error": "API key not configured"}), 500
        results = search_places(API_KEY, "Google", "Sydney NSW", limit=5)
        return jsonify({"status": "success", "response": {"places": results}})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/search", methods=["POST"])
def search():
    try:
        data = request.json
        query = data.get("query", "equipment hire")
        location = data.get("location", "Sydney NSW")
        limit = min(int(data.get("limit", 50)), 5000)

        if not API_KEY:
            return jsonify({"error": "API key not configured"}), 500

        results = search_places(
            API_KEY,
            query,
            location,
            limit,
            cities=data.get("cities"),
            state_code=data.get("state"),
        )

        return jsonify(
            {
                "success": True,
                "count": len(results),
                "query": query,
                "location": location,
                "results": results,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scrape-emails", methods=["POST"])
def scrape_emails():
    try:
        data = request.json
        results = data.get("results", [])
        if not results:
            return jsonify({"error": "No results provided"}), 400
        scrape_emails_from_websites(results)
        return jsonify({"success": True, "count": len(results), "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs", methods=["POST"])
def create_job():
    global job_counter
    try:
        data = request.json
        job_counter += 1
        job = {
            "id": job_counter,
            "query": data.get("query", "equipment hire"),
            "locations": data.get("locations", ["Sydney NSW"]),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "results": [],
            "progress": 0,
        }
        jobs[job_counter] = job
        return jsonify(job), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/export/<int:job_id>/csv", methods=["GET"])
def export_csv(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    csv_lines = [
        "#,Business Name,Address,City,State,Postcode,Phone,Website,Maps,Domain"
    ]
    for i, result in enumerate(job.get("results", []), 1):
        csv_lines.append(
            f'{i},"{result.get("name", "")}","{result.get("address", "")}",'
            f'"{result.get("city", "")}","{result.get("state", "")}",'
            f'"{result.get("postcode", "")}","{result.get("phone", "")}",'
            f'"{result.get("website", "")}","{result.get("maps_url", "")}",'
            f'"{result.get("domain", "")}"'
        )

    csv_content = "\n".join(csv_lines)
    today = date.today().isoformat()
    filename = f"{today}_export.csv"
    return (
        csv_content,
        200,
        {
            "Content-Type": "text/csv",
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="127.0.0.1", port=5001, debug=debug)
