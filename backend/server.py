import os
from pathlib import Path
import requests
from flask import Flask, request, session, jsonify, send_from_directory, redirect
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv
from life_wrapped.stats import bucket_by_month, monthly_summary
from life_wrapped.renderers.calendar_heatmap import (
    generate_calendar_heatmaps,
    OUTPUTS_DIR as HEATMAP_OUTPUTS_DIR,
)
from urllib.parse import urlencode


# Load environment variables from .env (for local Heroku CLI testing)
load_dotenv()

app = Flask(__name__)

# Sessions stored server-side (in Heroku ephemeral filesystem)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True  # enforce HTTPS-only cookies
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

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
OUTPUTS_DIR = HEATMAP_OUTPUTS_DIR

# ---------- Spotify Authorization ---------- #

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_RECENT_URL = "https://api.spotify.com/v1/me/top/tracks"

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_SCOPE = "user-top-read user-read-recently-played"


def refresh_spotify_token():
    refresh_token = session.get("spotify_refresh_token")
    if not refresh_token:
        app.logger.warning("Spotify refresh token missing from session")
        return None

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    resp = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    if resp.status_code != 200:
        app.logger.warning("Spotify token refresh failed: %s", resp.text)
        return None

    data = resp.json()
    access_token = data.get("access_token")
    if access_token:
        session["spotify_access_token"] = access_token
    if data.get("refresh_token"):
        session["spotify_refresh_token"] = data["refresh_token"]
    return access_token

@app.route("/auth/login")
def auth_login():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_REDIRECT_URI:
        return jsonify({"error": "Spotify credentials missing"}), 500
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPE,
    }
    return redirect(f"{SPOTIFY_AUTH_URL}?{urlencode(params)}")


@app.route("/auth/callback")
def auth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No code"}), 400

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    app.logger.info(f"Spotify token payload: {payload}")
    resp = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    data = resp.json()

    if "access_token" not in data:
        return jsonify(data), 400

    session["spotify_access_token"] = data["access_token"]
    session["spotify_refresh_token"] = data.get("refresh_token")

    # Redirect back to React with a query flag
    return redirect("/?spotify=1")


@app.route("/api/summary")
def spotify_summary():
    token = session.get("spotify_access_token")
    if not token:
        return jsonify({"error": "unauthorized"}), 401

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(SPOTIFY_RECENT_URL, headers=headers, params={"limit": 3, "time_range": "short_term"})

    if resp.status_code == 401:
        refreshed_token = refresh_spotify_token()
        if not refreshed_token:
            return jsonify({"error": "spotify_token_expired"}), 401
        headers["Authorization"] = f"Bearer {refreshed_token}"
        resp = requests.get(SPOTIFY_RECENT_URL, headers=headers, params={"limit": 50})

    if resp.status_code != 200:
        app.logger.warning(
            "Spotify recently played request failed (%s): %s",
            resp.status_code,
            resp.text,
        )
        return jsonify({"error": "spotify_api_error"}), resp.status_code

    data = resp.json()

    top_tracks = []
    for rank, item in enumerate(data.get("items", []), start=1):
        top_tracks.append({
            "rank": rank,
            "track": item["name"],
            "artist": ", ".join([artist["name"] for artist in item["artists"]]),
            "album": item["album"]["name"],
            "spotify_url": item["external_urls"]["spotify"],
            "cover_art": item["album"]["images"][0]["url"] if item["album"]["images"] else None,

        })
    session["spotify_summary"] = top_tracks
    return jsonify({"spotify_summary": top_tracks})


@app.route("/outputs/<path:filename>")
def serve_outputs(filename):
    return send_from_directory(str(OUTPUTS_DIR), filename)


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
    buckets = bucket_by_month(days)
    app.logger.info("/upload: bucketed into %d months", len(buckets))
    summaries = [monthly_summary(bucket) for bucket in buckets]
    app.logger.info("/upload: generated %d monthly summaries", len(summaries))

    heatmaps = generate_calendar_heatmaps(buckets, output_dir=OUTPUTS_DIR)
    app.logger.info("/upload: generated %d calendar heatmaps", len(heatmaps))

    session["last_summary"] = {
        "filename": file.filename,
        "summaries": summaries,
        "heatmaps": heatmaps,
    }
    response_payload = {
        **session["last_summary"],
        "spotify_summary": session.get("spotify_summary", []),
    }
    return jsonify(response_payload)


@app.route("/api/last-summary")
def last_summary():
    last = session.get("last_summary")
    if not last:
        return jsonify({"error": "No summary available"}), 404
    response_payload = {
        **last,
        "spotify_summary": session.get("spotify_summary", []),
    }
    return jsonify(response_payload)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path: str):
    if path:
        target = BUILD_DIR / path
        if target.is_file():
            return send_from_directory(str(BUILD_DIR), path)

    return send_from_directory(str(BUILD_DIR), "index.html")
