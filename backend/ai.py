import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_quiz(subject):
    prompt = f"""
Generate 7 MCQ questions on {subject}.

Return ONLY in JSON format like this:
[
  {{
    "question": "....",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Do not add any extra text.
"""

    response = model.generate_content(prompt)
    return response.text