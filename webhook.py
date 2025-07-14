from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MongoDB setup
uri = "mongodb+srv://<your-username>:<your-password>@cluster0.jmva0l3.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
db = client["test_database"]
collection = db["test_collection"]

@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.json

    try:
        author = payload.get("sender", {}).get("login", "Unknown")
        timestamp = datetime.utcnow().isoformat()

        if event_type == "push":
            to_branch = payload.get("ref", "").split("/")[-1]
            from_branch = ""
        elif event_type == "pull_request":
            from_branch = payload["pull_request"]["head"]["ref"]
            to_branch = payload["pull_request"]["base"]["ref"]
        elif event_type == "merge":
            from_branch = payload["pull_request"]["head"]["ref"]
            to_branch = payload["pull_request"]["base"]["ref"]
        else:
            from_branch = ""
            to_branch = ""

        document = {
            "type": event_type,
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        collection.insert_one(document)
        return jsonify({"message": "Event stored"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
