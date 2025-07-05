from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# MongoDB Atlas connection string
client = MongoClient("mongodb+srv://gudiputisangeetha:52neFH8edv8aKemN@cluster0.jmva0l3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client["webhook_db"]
collection = db["events"]

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")
    timestamp = datetime.utcnow()

    if event_type == "push":
        author = data["pusher"]["name"]
        to_branch = data["ref"].split("/")[-1]

        event = {
            "event_type": "push",
            "author": author,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

    elif event_type == "pull_request":
        action = data.get("action")
        if action == "opened":
            author = data["pull_request"]["user"]["login"]
            from_branch = data["pull_request"]["head"]["ref"]
            to_branch = data["pull_request"]["base"]["ref"]

            event = {
                "event_type": "pull_request",
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp
            }

        elif action == "closed" and data["pull_request"]["merged"]:
            author = data["pull_request"]["user"]["login"]
            from_branch = data["pull_request"]["head"]["ref"]
            to_branch = data["pull_request"]["base"]["ref"]

            event = {
                "event_type": "merge",
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp
            }
        else:
            return jsonify({"message": "Ignored pull_request action"}), 200

    else:
        return jsonify({"message": "Event ignored"}), 200

    collection.insert_one(event)
    return jsonify({"message": "Event stored"}), 201

@app.route("/events", methods=["GET"])
def get_events():
    results = collection.find().sort("timestamp", -1).limit(20)
    events = []
    for r in results:
        r["_id"] = str(r["_id"])
        r["timestamp"] = r["timestamp"].strftime("%d %B %Y - %I:%M %p UTC")
        events.append(r)
    return jsonify(events)

if __name__ == "__main__":
    app.run(debug=True)
