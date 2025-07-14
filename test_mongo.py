from pymongo import MongoClient
from datetime import datetime, timezone

uri = "mongodb+srv://gudiputisangeetha:52neFH8edv8aKemN@cluster0.jmva0l3.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["test_database"]
collection = db["test_collection"]

# Optional: Clear old test data
collection.delete_many({"source": "test_script"})

# Insert properly formatted documents
collection.insert_many([
    {
        "type": "push",
        "author": "Travis",
        "to_branch": "staging",
        "timestamp": datetime.now(timezone.utc),
        "source": "test_script"
    },
    {
        "type": "pull_request",
        "author": "Travis",
        "from_branch": "staging",
        "to_branch": "master",
        "timestamp": datetime.now(timezone.utc),
        "source": "test_script"
    },
    {
        "type": "merge",
        "author": "Travis",
        "from_branch": "dev",
        "to_branch": "master",
        "timestamp": datetime.now(timezone.utc),
        "source": "test_script"
    }
])

print("✅ Test events inserted successfully.")
