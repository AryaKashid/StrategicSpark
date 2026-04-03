import jwt
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import users_collection, quiz_collection, quiz_history_collection
from ai import generate_quiz, analyze_performance

app = Flask(__name__)
# Allow cross origin requests from our frontend
CORS(app)

from functools import wraps

app.config['SECRET_KEY'] = 'your_super_secret_key_here' 

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Handle Bearer token format
            if token.startswith('Bearer '):
                token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users_collection.find_one({'email': data['user']})
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/")
def home():
    return render_template("auth.html")   

DOMAIN_DATA = {
    "medical": {
        "title": "Medical",
        "description": "MBBS, Pharmacy & Healthcare Management",
        "icon": "🩺",
        "topics": [
            {"name": "Anatomy", "icon": "🦴", "desc": "Study of biological structures."},
            {"name": "Pharmacology", "icon": "💊", "desc": "Drug interactions and uses."}
        ],
        "courses": {
            "beginner": [
                {"title": "Anatomy & Physiology for Beginners", "platform": "Coursera", "link": "https://www.coursera.org/learn/anatomy"},
                {"title": "Medical Terminology 101", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "intermediate": [
                {"title": "Advanced Anatomy", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Clinical Pharmacology", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "pro": [
                {"title": "Surgical Assistant Masterclass", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Healthcare Management Pro", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ]
        }
    },
    "engineering": {
        "title": "Engineering",
        "description": "Electrical, Mechanical, Civil & Robotics",
        "icon": "⚙️",
        "topics": [
            {"name": "Thermodynamics", "icon": "🔥", "desc": "Heat and temperature physics."},
            {"name": "Robotics", "icon": "🤖", "desc": "Automated machine design."}
        ],
        "courses": {
            "beginner": [
                {"title": "Engineering Fundamentals", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Intro to Robotics", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "intermediate": [
                {"title": "Robotics: Design and Control", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Advanced Thermodynamics", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "pro": [
                {"title": "Industrial Robot Integration", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Fluid Dynamics in Engineering", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ]
        }
    },
    "cs-it": {
        "title": "CS & IT",
        "description": "Software, AI, Cyber Security & Data Science",
        "icon": "💻",
        "topics": [
            {"name": "Python", "icon": "🐍", "desc": "General-purpose & AI programming."},
            {"name": "React", "icon": "⚛️", "desc": "Modern UI library."}
        ],
        "courses": {
            "beginner": [
                {"title": "Python for Everybody", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Web Development Bootcamp", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "intermediate": [
                {"title": "Data Structures & Algorithms", "platform": "GFG", "link": "https://www.geeksforgeeks.org/"},
                {"title": "React - The Complete Guide", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "pro": [
                {"title": "Architecting on AWS", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Advanced Machine Learning", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ]
        }
    },
    "commerce": {
        "title": "Commerce",
        "description": "Accounting, CA, CS & Financial Analysis",
        "icon": "📊",
        "topics": [
            {"name": "Accounting", "icon": "📒", "desc": "Financial record keeping."},
            {"name": "Economics", "icon": "📈", "desc": "Market trends and theories."}
        ],
        "courses": {
            "beginner": [
                {"title": "Bookkeeping Basics", "platform": "Udemy", "link": "https://www.udemy.com/"},
                {"title": "Intro to Microeconomics", "platform": "Coursera", "link": "https://www.coursera.org/"}
            ],
            "intermediate": [
                {"title": "Financial Statement Analysis", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Intermediate Macroeconomics", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "pro": [
                {"title": "Investment Management Spezialization", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Taxation Strategies for Biz", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ]
        }
    },
    "mba": {
        "title": "MBA / Mgmt",
        "description": "Marketing, HR, Operations & Strategy",
        "icon": "👔",
        "topics": [
            {"name": "Marketing", "icon": "🎯", "desc": "Brand and product promotion."},
            {"name": "Leadership", "icon": "👑", "desc": "Strategic organizational management."}
        ],
        "courses": {
            "beginner": [
                {"title": "Marketing Fundamentals", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "Introduction to Leadership", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "intermediate": [
                {"title": "Strategic Management", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "HR Analytics", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ],
            "pro": [
                {"title": "Executive MBA Specialization", "platform": "Coursera", "link": "https://www.coursera.org/"},
                {"title": "International Business Strategy", "platform": "Udemy", "link": "https://www.udemy.com/"}
            ]
        }
    }
}

@app.route("/choice")
def choice():
    return render_template("choice.html")

@app.route("/levels")
def levels():
    return render_template("levels.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/learning")
def learning():
    return render_template("learning.html")

@app.route("/domain/<domain_id>")
def domain_view(domain_id):
    if domain_id not in DOMAIN_DATA:
        return "Domain not found", 404
    mode = request.args.get('mode', 'quiz')
    level = request.args.get('level', 'beginner')
    
    domain = DOMAIN_DATA[domain_id]
    courses = []
    if mode == 'learn' and 'courses' in domain:
        courses = domain['courses'].get(level, [])
        
    return render_template("domain.html", domain=domain, domain_id=domain_id, mode=mode, level=level, courses=courses)


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
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
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

@app.route("/api/quiz/generate", methods=["POST"])
@token_required
def api_generate_quiz(current_user):
    data = request.json
    topic = data.get("topic")
    if not topic:
        return jsonify({"message": "Topic is required"}), 400
    
    # Check if this topic has been attempted before
    previous_attempt = quiz_history_collection.find_one({
        "user_email": current_user["email"],
        "topic": topic
    })
    
    level = "beginner"
    if previous_attempt:
        # If they've already tried it, we could level them up, 
        # but for now let's just use 'intermediate' as the next step
        level = "intermediate"
        
    questions = generate_quiz(topic, level)
    
    if not questions:
        return jsonify({"message": "AI could not generate questions. Try again."}), 500
        
    return jsonify({
        "questions": questions,
        "level": level
    })

@app.route("/api/quiz/submit", methods=["POST"])
@token_required
def api_submit_quiz(current_user):
    data = request.json
    topic = data.get("topic")
    user_answers = data.get("answers") # List of strings
    questions = data.get("questions") # List of question objects
    
    if not all([topic, user_answers, questions]):
        return jsonify({"message": "Missing quiz data"}), 400
        
    # Calculate score
    score = 0
    results = []
    for i, q in enumerate(questions):
        is_correct = (user_answers[i] == q["answer"])
        if is_correct:
            score += 1
        results.append({
            "question": q["question"],
            "user_answer": user_answers[i],
            "correct_answer": q["answer"],
            "is_correct": is_correct
        })
    
    # Generate AI Analysis
    analysis = analyze_performance(topic, score, results)
    
    # Save to history
    quiz_attempt = {
        "user_email": current_user["email"],
        "topic": topic,
        "score": score,
        "total_questions": len(questions),
        "results": results,
        "analysis": analysis,
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    }
    quiz_history_collection.insert_one(quiz_attempt)
    
    return jsonify({
        "score": score,
        "total": len(questions),
        "analysis": analysis,
        "results": results
    })

@app.route("/quiz_page")
def quiz_page():
    return render_template("quiz.html")

if __name__ == "__main__":
    app.run(debug=True)