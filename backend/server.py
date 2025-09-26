from flask import Flask, request, jsonify
from life_wrapped import io, stats
import tempfile

app = Flask(__name__)
@app.route("/upload", methods=["POST"])

def upload():
    file = request.files["file"]
    if not file:
        return "No file uploaded", 400

    # save file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        file.save(tmp.name)
        path = tmp.name

    # run your pipeline
    days = io.load_days_from_excel(path)
    buckets = stats.bucket_by_month(days)
    summaries = [stats.monthly_summary(m).__dict__ for m in buckets]

    return jsonify(summaries)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
