import sys
import tempfile
from pathlib import Path

from flask import Flask, request, jsonify

from life_wrapped import io, stats
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/upload")

def upload():
    file = request.files["file"]
    if not file:
        return jsonify({"error": "no file"}), 400

    # run your pipeline here...
    return jsonify([{"message": "File uploaded", "filename": file.filename}])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
