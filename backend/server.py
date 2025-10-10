import os
from pathlib import Path

import requests
from flask import Flask, redirect, request, session, jsonify, send_from_directory
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

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")  # must match Spotify dashboard

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_RECENT_URL = "https://api.spotify.com/v1/me/player/recently-played"
# Flask serve React dist folder
BUILD_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# ---------------- Spotify OAuth ---------------- #

@app.route("/auth/login")
def login():
    app.logger.info("/auth/login: redirecting to Spotify auth")
    scope = "user-read-recently-played"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scope,
    }
    app.logger.debug("/auth/login params: %s", params)
    query = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
    return redirect(f"{SPOTIFY_AUTH_URL}?{query}")


@app.route("/auth/callback")
def callback():
    app.logger.info("/auth/callback: received request")
    code = request.args.get("code")
    if not code:
        app.logger.error("/auth/callback: missing code param")
        return "No code returned", 400
    app.logger.debug("/auth/callback: code=%s", code[:10] + "...")

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    app.logger.debug("/auth/callback payload: %s", {k: ('***' if 'secret' in k else v) for k, v in payload.items()})
    resp = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    app.logger.info("/auth/callback: token endpoint status %s", resp.status_code)
    data = resp.json()

    if "access_token" not in data:
        app.logger.error("/auth/callback: access_token missing. Response: %s", data)
        return jsonify(data), 400

    session["access_token"] = data["access_token"]
    session["refresh_token"] = data.get("refresh_token")
    app.logger.info("/auth/callback: stored access & refresh tokens")

    # Fetch Spotify data
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    r = requests.get(SPOTIFY_RECENT_URL, headers=headers, params={"limit": 50})
    app.logger.info("/auth/callback: recently-played status %s", r.status_code)
    if r.status_code == 200:
        items = r.json().get("items", [])
        app.logger.debug("/auth/callback: fetched %d recent items", len(items))
        monthly_counts = {}
        for item in items:
            month = item["played_at"][:7]
            track = item["track"]["name"]
            monthly_counts.setdefault(month, {})
            monthly_counts[month][track] = monthly_counts[month].get(track, 0) + 1

        top_tracks = {
            m: max(counts.items(), key=lambda x: x[1])
            for m, counts in monthly_counts.items()
        }
        app.logger.debug("/auth/callback: top tracks %s", top_tracks)
        session["spotify_summary"] = {
            month: {"track": track, "plays": plays}
            for month, (track, plays) in top_tracks.items()
        }

        session["last_summary"] = session.get("last_summary", {})
        session["last_summary"]["spotify_summary"] = session["spotify_summary"]

    # Redirect back to your deployed frontend
    app.logger.info("/auth/callback: redirecting to %s", FRONTEND_URL)
    return redirect(f"{FRONTEND_URL}?spotify=1")


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
        "spotify_summary": session.get("spotify_summary", {}),
    }
    return jsonify(session["last_summary"])


@app.route("/api/last-summary")
def last_summary():
    if "last_summary" not in session:
        return jsonify({"error": "No summary available"}), 404
    return jsonify(session["last_summary"])


@app.route("/api/summary")
def spotify_summary():
    if "access_token" not in session:
        return jsonify({"error": "Not logged into Spotify"}), 401
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    resp = requests.get(SPOTIFY_RECENT_URL, headers=headers, params={"limit": 50})
    return jsonify(resp.json()), resp.status_code


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path: str):
    if path:
        target = BUILD_DIR / path
        if target.is_file():
            return send_from_directory(str(BUILD_DIR), path)

    return send_from_directory(str(BUILD_DIR), "index.html")
