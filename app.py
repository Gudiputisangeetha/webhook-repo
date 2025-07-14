from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)
CORS(app)

# MongoDB connection
uri = "mongodb+srv://gudiputisangeetha:52neFH8edv8aKemN@cluster0.jmva0l3.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    db = client["test_database"]
    collection = db["test_collection"]
    print("✅ Connected in app.py")
except Exception as e:
    print("❌ Connection error in app.py:", e)
    collection = None

# Endpoint: GET /events
@app.route("/events", methods=["GET"])
def get_events():
    if collection is None:
        return jsonify({"error": "MongoDB not connected"}), 500
    try:
        events = list(collection.find().sort("_id", -1))
        print(f"📤 Sending {len(events)} documents")
        return dumps(events), 200
    except Exception as e:
        print("❌ Error fetching events:", str(e))
        return jsonify({"error": str(e)}), 500

# Endpoint: POST /webhook
@app.route("/webhook", methods=["POST"])
def receive_webhook():
    if collection is None:
        return jsonify({"error": "MongoDB not connected"}), 500

    try:
        data = request.json
        event_type = request.headers.get("X-GitHub-Event")
        author = data.get("pusher", {}).get("name") or data.get("sender", {}).get("login")

        if event_type == "push":
            doc = {
                "type": "push",
                "author": author,
                "to_branch": data["ref"].split("/")[-1],
                "timestamp": data["head_commit"]["timestamp"]
            }

        elif event_type == "pull_request":
            action = data["action"]
            pr = data["pull_request"]
            if action == "opened":
                doc = {
                    "type": "pull_request",
                    "author": author,
                    "from_branch": pr["head"]["ref"],
                    "to_branch": pr["base"]["ref"],
                    "timestamp": pr["created_at"]
                }
            elif action == "closed" and pr.get("merged"):
                doc = {
                    "type": "merge",
                    "author": author,
                    "from_branch": pr["head"]["ref"],
                    "to_branch": pr["base"]["ref"],
                    "timestamp": pr["merged_at"]
                }
            else:
                return jsonify({"message": "PR event ignored"}), 200
        else:
            return jsonify({"message": "Event ignored"}), 200

        collection.insert_one(doc)
        print("✅ Event stored:", doc)
        return jsonify({"message": "Stored"}), 201

    except Exception as e:
        print("❌ Error in /webhook:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
