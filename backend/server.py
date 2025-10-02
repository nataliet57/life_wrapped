import tempfile

from flask import Flask, redirect, request, session, jsonify, url_for
from flask_cors import CORS # remove this once i push to prod
from life_wrapped import io, stats

app = Flask(__name__)
CORS(app) # remove

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
  scope = "read-recently-played"
  auth_url = (
    f"{SPOTIFY_AUTH_URL}"
  )

@app.get("/")
def health():
    return {"status": "ok"}

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

    return jsonify({
        "filename": file.filename,
        "summaries": summaries,
    })




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

