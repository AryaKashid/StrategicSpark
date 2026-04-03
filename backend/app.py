import jwt
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import users_collection, quiz_collection

app = Flask(__name__)
# Allow cross origin requests from our frontend
CORS(app)

app.config['SECRET_KEY'] = 'your_super_secret_key_here' 

# @app.route("/")
# def home():
#     return "MongoDB Connected"
@app.route("/")
def home():
    return render_template("auth.html")   

DOMAIN_DATA = {
    "medical": {
        "title": "Medical",
        "description": "MBBS, Pharmacy & Healthcare Management",
        "icon": "🩺",
        "topics": [
            {"name": "Anatomy Basics", "icon": "🦴", "desc": "Study of biological structures."},
            {"name": "Pharmacology", "icon": "💊", "desc": "Drug interactions and uses."},
            {"name": "First Aid", "icon": "🚑", "desc": "Emergency medical treatments."},
            {"name": "Healthcare Ethics", "icon": "⚖️", "desc": "Moral principles in medicine."}
        ]
    },
    "engineering": {
        "title": "Engineering",
        "description": "Electrical, Mechanical, Civil & Robotics",
        "icon": "⚙️",
        "topics": [
            {"name": "Thermodynamics", "icon": "🔥", "desc": "Heat and temperature physics."},
            {"name": "Circuits", "icon": "⚡", "desc": "Electrical system fundamentals."},
            {"name": "Robotics", "icon": "🤖", "desc": "Automated machine design."},
            {"name": "AutoCAD", "icon": "📐", "desc": "Computer-Aided Design software."}
        ]
    },
    "cs-it": {
        "title": "CS & IT",
        "description": "Software, AI, Cyber Security & Data Science",
        "icon": "💻",
        "topics": [
            {"name": "HTML & CSS", "icon": "🌐", "desc": "Web design foundation."},
            {"name": "JavaScript", "icon": "⚡", "desc": "Interactive web logic."},
            {"name": "Python", "icon": "🐍", "desc": "General-purpose & AI programming."},
            {"name": "Java", "icon": "☕", "desc": "Enterprise application development."},
            {"name": "React", "icon": "⚛️", "desc": "Modern UI library."}
        ]
    },
    "commerce": {
        "title": "Commerce",
        "description": "Accounting, CA, CS & Financial Analysis",
        "icon": "📊",
        "topics": [
            {"name": "Accounting", "icon": "📒", "desc": "Financial record keeping."},
            {"name": "Economics", "icon": "📈", "desc": "Market trends and theories."},
            {"name": "Business Law", "icon": "⚖️", "desc": "Legal aspects of trade."},
            {"name": "Taxation", "icon": "💰", "desc": "Income and corporate tax rules."}
        ]
    },
    "mba": {
        "title": "MBA / Mgmt",
        "description": "Marketing, HR, Operations & Strategy",
        "icon": "👔",
        "topics": [
            {"name": "Marketing", "icon": "🎯", "desc": "Brand and product promotion."},
            {"name": "HR Mgmt", "icon": "🤝", "desc": "Managing workplace talent."},
            {"name": "Operations", "icon": "🏭", "desc": "Supply chain and efficiency."},
            {"name": "Leadership", "icon": "👑", "desc": "Strategic organizational management."}
        ]
    },
    "iti": {
        "title": "ITI / Tech",
        "description": "Vocational training & Technical trades",
        "icon": "🔧",
        "topics": [
            {"name": "Electrician", "icon": "🔌", "desc": "Wiring and installation."},
            {"name": "Plumbing", "icon": "🚰", "desc": "Pipes and fluid systems."},
            {"name": "Welding", "icon": "🔥", "desc": "Metal fusion techniques."},
            {"name": "Carpentry", "icon": "🪚", "desc": "Woodworking and structures."}
        ]
    },
    "science": {
        "title": "Science",
        "description": "Physics, Chemistry, Biology & Research",
        "icon": "🧪",
        "topics": [
            {"name": "Physics", "icon": "⚛️", "desc": "Matter and energy laws."},
            {"name": "Organic Chemistry", "icon": "🔬", "desc": "Carbon-based compounds."},
            {"name": "Biology", "icon": "🧬", "desc": "Study of living organisms."},
            {"name": "Env Science", "icon": "🌍", "desc": "Ecology and environment."}
        ]
    },
    "others": {
        "title": "Others",
        "description": "Law, Arts, Design & Competitive Exams",
        "icon": "🎨",
        "topics": [
            {"name": "Graphic Design", "icon": "🖌️", "desc": "Visual communication arts."},
            {"name": "History", "icon": "📜", "desc": "Study of past events."},
            {"name": "Law Basics", "icon": "🏛️", "desc": "Legal system overview."},
            {"name": "Foreign Languages", "icon": "🗣️", "desc": "Linguistic skills development."}
        ]
    }
}

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/domain/<domain_id>")
def domain_view(domain_id):
    if domain_id not in DOMAIN_DATA:
        return "Domain not found", 404
    return render_template("domain.html", domain=DOMAIN_DATA[domain_id])

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
        "role": data.get("role", "student") 
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