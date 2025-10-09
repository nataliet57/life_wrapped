import os
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
CORS(
    app,
    resources={r"/*": {"origins": [FRONTEND_URL]}},
    supports_credentials=True,
)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")  # must match Spotify dashboard

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_RECENT_URL = "https://api.spotify.com/v1/me/player/recently-played"
# Flask serve React dist folder
BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")

@app.route("/")
def index():
    return jsonify({"message": "Life Wrapped Flask backend is running!"})

# ---------------- Spotify OAuth ---------------- #

@app.route("/auth/login")
def login():
    scope = "user-read-recently-played"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scope,
    }
    query = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
    return redirect(f"{SPOTIFY_AUTH_URL}?{query}")


@app.route("/auth/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code returned", 400

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

    session["access_token"] = data["access_token"]
    session["refresh_token"] = data.get("refresh_token")

    # Fetch Spotify data
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    r = requests.get(SPOTIFY_RECENT_URL, headers=headers, params={"limit": 50})
    if r.status_code == 200:
        items = r.json().get("items", [])
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
        session["spotify_summary"] = {
            month: {"track": track, "plays": plays}
            for month, (track, plays) in top_tracks.items()
        }

        session["last_summary"] = session.get("last_summary", {})
        session["last_summary"]["spotify_summary"] = session["spotify_summary"]

    # Redirect back to your deployed frontend
    return redirect(f"{FRONTEND_URL}?spotify=1")


# ---------------- Upload & API ---------------- #

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]

    from life_wrapped.io import load_days_from_excel
    from life_wrapped.stats import monthly_summary

    days = load_days_from_excel(file)
    summaries = [monthly_summary(m) for m in days]

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
def serve(path):
    if path != "" and os.path.exists(os.path.join(BUILD_DIR, path)):
        return send_from_directory(BUILD_DIR, path)
    else:
        return send_from_directory(BUILD_DIR, "index.html")
