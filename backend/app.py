from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# ==============================
# MongoDB Connection
# ==============================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/")

client = MongoClient(MONGO_URI)
db = client["cloaknote"]
collection = db["events"]

# ==============================
# Health Check API
# ==============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "service": "cloaknote-backend"
    })

# ==============================
# Track Event API
# ==============================
@app.route("/api/track", methods=["POST"])
def track_event():
    try:
        data = request.get_json()

        if not data or "event" not in data:
            return jsonify({"error": "Invalid payload"}), 400

        event_data = {
            "event": data["event"],
            "timestamp": datetime.utcnow(),
            "ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent")
        }

        collection.insert_one(event_data)

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================
# Get Stats API
# ==============================
@app.route("/api/stats", methods=["GET"])
def get_stats():
    try:
        total = collection.count_documents({})

        created = collection.count_documents({"event": "note_created"})
        viewed = collection.count_documents({"event": "note_viewed"})
        copied = collection.count_documents({"event": "link_copied"})

        return jsonify({
            "total_events": total,
            "notes_created": created,
            "notes_viewed": viewed,
            "links_copied": copied
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)