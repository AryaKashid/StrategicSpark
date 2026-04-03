import jwt
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import users_collection, quiz_collection

app = Flask(__name__)
# Allow cross origin requests from our frontend
CORS(app)

app.config['SECRET_KEY'] = 'your_super_secret_key_here' # In production, use environment variable

# @app.route("/")
# def home():
#     return "MongoDB Connected"
@app.route("/")
def home():
    return render_template("auth.html")   # Login page as homepage

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    if not data or not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"message": "Missing required fields"}), 400
        
    # Check if user already exists
    if users_collection.find_one({"email": data.get("email")}):
        return jsonify({"message": "User already exists!"}), 409
        
    hashed_password = generate_password_hash(data.get("password"))
    
    users_collection.insert_one({
        "name": data.get("name"),
        "email": data.get("email"),
        "password": hashed_password,
        "role": data.get("role", "student") # Default role
    })
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing required fields"}), 400
        
    user = users_collection.find_one({"email": data.get("email")})
    
    if user and check_password_hash(user["password"], data.get("password")):
        # Generate JWT Token
        token = jwt.encode({
            'user': user["email"],
            'name': user["name"],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            "message": "Login Successful",
            "token": token,
            "user": {"name": user["name"], "email": user["email"], "role": user.get("role", "student")}
        }), 200
        
    return jsonify({"message": "Invalid email or password"}), 401

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

from ai import generate_quiz

@app.route("/quiz/<subject>")
def quiz(subject):
    data = generate_quiz(subject)
    return data

@app.route("/test-ai")
def test_ai():
    result = generate_quiz("HTML")
    return result
    
if __name__ == "__main__":
    app.run(debug=True)