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
    Each question should have 4 options and correct answer.
    """

    response = model.generate_content(prompt)
    return response.text