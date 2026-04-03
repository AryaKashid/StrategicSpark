import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["SSparks_db"]
users_collection = db["users"]
quiz_collection = db["quiz"]
quiz_history_collection = db["quiz_history"]