import tempfile
import os
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request, session, jsonify, url_for
from flask_cors import CORS
from life_wrapped import io, stats
from dotenv import load_dotenv
from flask_session import Session

load_dotenv()

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

Session(app)
# cross origin reference sharing only needed developing locally 
# browsers block requests from http://localhost:5173 (React app) to http://127.0.0.1:5000 (Flask app)

CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True,
)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5000/auth/callback")

# Spotify endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_RECENT_URL = "https://api.spotify.com/v1/me/player/recently-played"

@app.route("/auth/login")
# https://developer.spotify.com/documentation/web-api/concepts/authorization
def login():
  scope = "user-read-recently-played"
  params = {
      "client_id": SPOTIFY_CLIENT_ID,
      "response_type": "code",
      "redirect_uri": SPOTIFY_REDIRECT_URI,
      "scope": scope,
  }
  return redirect(f"{SPOTIFY_AUTH_URL}?{urlencode(params)}")

@app.route("/auth/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code returned", 400

    # Exchange code for tokens
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    resp = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    data = resp.json()

    if "access_token" not in data:
        return jsonify(data), 400

    # Save tokens in session
    session["access_token"] = data["access_token"]
    session["refresh_token"] = data.get("refresh_token")
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    r = requests.get(SPOTIFY_RECENT_URL, headers=headers, params={"limit": 50})
    if r.status_code == 200:
        items = r.json().get("items", [])
        monthly_counts = {}
        for item in items:
            month = item["played_at"][:7]  # YYYY-MM
            track = item["track"]["name"]
            monthly_counts.setdefault(month, {})
            monthly_counts[month][track] = monthly_counts[month].get(track, 0) + 1

        top_tracks = {
            m: max(counts.items(), key=lambda x: x[1])
            for m, counts in monthly_counts.items()
        }
        # stash Spotify summary
        session["spotify_summary"] = {
            month: {"track": track, "plays": plays}
            for month, (track, plays) in top_tracks.items()
        }

        # merge into last_summary if exists
        if "last_summary" in session:
            session["last_summary"]["spotify_summary"] = session["spotify_summary"]

    # redirect back to frontend
    return redirect("http://localhost:5173/")


@app.route("/api/summary")
def summary():
    access_token = session.get("access_token")
    if not access_token:
        return jsonify({"error": "Not logged in"}), 401

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": 50}
    resp = requests.get(SPOTIFY_RECENT_URL, headers=headers, params=params)

    if resp.status_code != 200:
        return jsonify({"error": "Spotify API call failed", "details": resp.json()}), 400

    data = resp.json()
    items = data.get("items", [])

    # Example: group tracks by month-year and count frequency
    summary = {}
    for item in items:
        played_at = item["played_at"][:7]
        track_name = item["track"]["name"]
        summary.setdefault(played_at, {})
        summary[played_at][track_name] = summary[played_at].get(track_name, 0) + 1

    # Extract most listened track per month
    top_tracks = {}
    for month, counts in summary.items():
        top_track = max(counts.items(), key=lambda x: x[1])
        top_tracks[month] = {"track": top_track[0], "plays": top_track[1]}
    return jsonify({"spotify_summary": top_tracks})

        
@app.post("/upload")
def upload():
    file = request.files["file"]
    if not file:
        return jsonify({"error": "no file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        file.save(tmp.name)
        path = tmp.name

    days = io.load_days_from_excel(path)
    buckets = stats.bucket_by_month(days)
    summaries = [stats.monthly_summary(bucket) for bucket in buckets]

    session["last_summary"] = {
        "filename": file.filename,
        "summaries": summaries,
        "spotify_summary": session.get("spotify_summary", {})
    }

    return jsonify(session["last_summary"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
