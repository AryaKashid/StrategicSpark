import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def clean_json_response(text):
    """Securely extract JSON from Gemini's markdown response."""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*|\s*```', '', text)
    # Remove any leading/trailing non-JSON text
    start = text.find('[')
    end = text.rfind(']') + 1
    if start != -1 and end != 0:
        text = text[start:end]
    return text.strip()

def generate_quiz(subject, level="beginner"):
    prompt = f"""
Generate exactly 5 Multiple Choice Questions (MCQs) on the topic: {subject}.
Target Difficulty: {level}

Strict Requirements:
1. Return ONLY a valid JSON array.
2. Each object must have: "question", "options" (array of 4 strings), and "answer" (the exact string from the options).
3. Do not include any markdown formatting, triple backticks, or extra text.

Example Format:
[
  {{
    "question": "What is 2+2?",
    "options": ["3", "4", "5", "6"],
    "answer": "4"
  }}
]
"""

    try:
        response = model.generate_content(prompt)
        
        # Check if response has parts (safety check)
        if not response.parts:
            print("AI Safety Error: Response was blocked or empty.")
            return []
            
        text = response.text
        cleaned_data = clean_json_response(text)
        return json.loads(cleaned_data)
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return []

def analyze_performance(topic, score, results):
    """Analyze the user's quiz performance and provide a detailed roadmap in JSON format."""
    
    # Calculate accuracy and a mock precision for the UI
    total = len(results)
    accuracy = (score / total) * 100 if total > 0 else 0
    # Precision here is modeled as a factor of correct answers vs. topic confidence
    precision = (accuracy * 0.95) + (5 if accuracy > 50 else 2) # Just for UI visual variety
    if precision > 100: precision = 100

    prompt = f"""
You are an expert tutor. A student just finished a {total}-question quiz on {topic}.
Score: {score}/{total}
Detailed Results: {json.dumps(results)}

Tasks:
1. Provide a brief, encouraging 'summary' of their performance.
2. For each 'incorrect' answer in the results, provide a concise 'explanation' (max 2 sentences) of why their answer was wrong and what the correct concept is.
3. Provide 4-5 'recommendations' for courses or resources.
   - Include platforms: Udemy, Coursera, GeeksforGeeks, W3Schools, or NPTEL.
   - Each recommendation must have: "title", "platform", "link" (use a search link like 'https://www.udemy.com/courses/search/?q=' + topic), and "description".

Strict Requirement: Return ONLY a valid JSON object with this structure:
{{
  "summary": "...",
  "accuracy": {accuracy},
  "precision": {precision:.1f},
  "wrong_answers": [
    {{
      "question": "...",
      "user_answer": "...",
      "correct_answer": "...",
      "explanation": "..."
    }}
  ],
  "recommendations": [
    {{
      "title": "...",
      "platform": "...",
      "link": "...",
      "description": "..."
    }}
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text
        # Use our existing cleaner if needed, but the prompt is strict
        cleaned_data = text.strip()
        if "```json" in cleaned_data:
            cleaned_data = re.sub(r'```json\s*|\s*```', '', cleaned_data)
        
        # Ensure it's just the JSON object
        start = cleaned_data.find('{')
        end = cleaned_data.rfind('}') + 1
        if start != -1 and end != 0:
            cleaned_data = cleaned_data[start:end]
            
        return json.loads(cleaned_data)
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {
            "summary": "Great effort! Keep practicing to improve.",
            "accuracy": accuracy,
            "precision": precision,
            "wrong_answers": [],
            "recommendations": []
        }