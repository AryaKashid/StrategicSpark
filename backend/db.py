from pymongo import MongoClient

client = MongoClient("mongodb+srv://hackspark:8806926846@clusspark.qsbermf.mongodb.net/")

db = client["SSparks_db"]
users_collection = db["users"]
quiz_collection = db["quiz"]