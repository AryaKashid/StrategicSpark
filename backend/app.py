from flask import Flask, jsonify
from flask_cors import CORS
from db import users_collection, quiz_collection
from ai import generate_quiz

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "MongoDB Connected"

@app.route("/add")
def add():
    users_collection.insert_one({
        "name": "Arya",
        "role": "leader"
    })
    return "User added"

@app.route("/add-quiz")
def add_quiz():
    quiz_collection.insert_one({
        "question": "What is Python?",
        "options": ["Language", "Snake", "Game"],
        "answer": "Language"
    })
    return "Quiz added"

@app.route("/quiz/<subject>")
def quiz(subject):
    data = generate_quiz(subject)
    return jsonify({"quiz": data})   # ✅ FIXED

@app.route("/test-ai")
def test_ai():
    result = generate_quiz("HTML")
    return result

if __name__ == "__main__":
    app.run(debug=True)