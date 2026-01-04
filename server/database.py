import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
mongo_db = os.environ.get("MONGO_DB", "vitafuel")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)  # short timeout [ms]
try:
    client.admin.command("ping")  # confirms server reachable
    print("MongoDB connected")
except ConnectionFailure as e:
    print(f"MongoDB connection failed: {e}")
    print("Please make sure MongoDB is running on localhost:27017")

db = client[mongo_db]
