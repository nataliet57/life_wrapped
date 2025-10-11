import os
from pathlib import Path

from flask import Flask, request, session, jsonify, send_from_directory
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env (for local Heroku CLI testing)
load_dotenv()

app = Flask(__name__)

# Sessions stored server-side (in Heroku ephemeral filesystem)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True  # enforce HTTPS-only cookies

Session(app)

FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    CORS(
        app,
        resources={r"/*": {"origins": [FRONTEND_URL]}},
        supports_credentials=True,
    )
else:
    CORS(app, supports_credentials=True)

# Flask serve React dist folder
BUILD_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# ---------------- Upload & API ---------------- #

@app.route("/upload", methods=["POST"])
def upload():
    app.logger.info("/upload: received file upload")
    if "file" not in request.files:
        app.logger.warning("/upload: no file part in request")
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    app.logger.debug("/upload: file name %s", file.filename)

    from life_wrapped.io import load_days_from_excel
    from life_wrapped.stats import monthly_summary

    days = load_days_from_excel(file)
    app.logger.info("/upload: loaded %d day records", len(days))
    summaries = [monthly_summary(m) for m in days]
    app.logger.info("/upload: generated %d monthly summaries", len(summaries))

    session["last_summary"] = {
        "filename": file.filename,
        "summaries": summaries,
    }
    return jsonify(session["last_summary"])


@app.route("/api/last-summary")
def last_summary():
    if "last_summary" not in session:
        return jsonify({"error": "No summary available"}), 404
    return jsonify(session["last_summary"])

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path: str):
    if path:
        target = BUILD_DIR / path
        if target.is_file():
            return send_from_directory(str(BUILD_DIR), path)

    return send_from_directory(str(BUILD_DIR), "index.html")
