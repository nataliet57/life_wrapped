import tempfile

from flask import Flask, request, jsonify

from life_wrapped import io, stats

app = Flask(__name__)

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
