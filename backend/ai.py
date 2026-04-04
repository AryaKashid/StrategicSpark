import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# Using gemini-2.5-flash as per USER request
model = genai.GenerativeModel("gemini-2.5-flash")

def clean_json_response(text):
    """Securely extract JSON from Gemini's markdown response."""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*|\s*```', '', text)
    
    # Identify the potential JSON range
    start_curly = text.find('{')
    start_bracket = text.find('[')
    
    # Determine the earliest starting point
    if start_curly != -1 and (start_bracket == -1 or start_curly < start_bracket):
        start = start_curly
        end = text.rfind('}') + 1
    elif start_bracket != -1:
        start = start_bracket
        end = text.rfind(']') + 1
    else:
        return text.strip()
        
    if start != -1 and end > start:
        text = text[start:end]
    return text.strip()

def safe_generate(prompt):
    """Wrapper for Gemini content generation with robust 429 error handling."""
    try:
        response = model.generate_content(prompt)
        
        # Check if response was blocked or empty
        if not response.parts:
            return "ERROR_BLOCKED"
            
        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg:
            return "ERROR_RATE_LIMIT"
        print(f"Gemini API Error: {e}")
        return "ERROR_GENERIC"

def generate_quiz(subject, level="beginner"):
    prompt = f"""
Generate exactly 5 Multiple Choice Questions (MCQs) on the topic: {subject}.
Target Difficulty: {level}

Strict Requirements:
1. Return ONLY a valid JSON array.
2. Each object must have: "question", "options" (array of 4 strings), and "answer" (the exact string from the options).
3. Do not include any markdown formatting, triple backticks, or extra text.
"""

    raw_response = safe_generate(prompt)
    
    if raw_response in ["ERROR_RATE_LIMIT", "ERROR_BLOCKED", "ERROR_GENERIC"]:
        print(f"Quiz Generation Failed: {raw_response}")
        return []

    try:
        cleaned_data = clean_json_response(raw_response)
        return json.loads(cleaned_data)
    except Exception as e:
        print(f"JSON Parsing Error in Quiz Generation: {e}")
        return []

def analyze_performance(topic, score, results):
    """Analyze the user's quiz performance and provide a detailed roadmap in JSON format."""
    total = len(results)
    accuracy = (score / total) * 100 if total > 0 else 0
    
    prompt = f"""
You are an expert tutor. A student just finished a {total}-question quiz on {topic}.
Score: {score}/{total}
Detailed Results: {json.dumps(results)}

Tasks:
1. Provide a brief, encouraging 'summary' of their performance.
2. For each 'incorrect' answer in the results, provide a concise 'explanation' (max 2 sentences) of why their answer was wrong and what the correct concept is.
3. Provide 4-5 'recommendations' for courses or resources.
4. Identify the ONE most critical 'foundational_gap' (a simpler prerequisite concept) causing their mistakes.
5. Provide a 2-minute 'bridge_lesson' (max 100 words) using punchy ELI5 analogies.
6. Provide a 'youtube_query' for a 2-minute tutorial.

Strict Requirement: Return ONLY a valid JSON object with this structure:
{{
  "summary": "...",
  "accuracy": {accuracy},
  "mastery": 0-100,
  "wrong_answers": [ {{ "question": "...", "explanation": "..." }} ],
  "recommendations": [ {{ "title": "...", "platform": "...", "link": "...", "description": "..." }} ],
  "concept_weaver": {{ "foundational_gap": "...", "bridge_lesson": "...", "why_it_matters": "...", "youtube_query": "..." }}
}}
"""

    raw_response = safe_generate(prompt)
    
    # Fallback for Rate Limiting
    if raw_response == "ERROR_RATE_LIMIT":
        return {
            "error": "rate_limit",
            "summary": "The AI Mentor is currently handling too many requests. Please try again in 30 seconds.",
            "accuracy": accuracy,
            "mastery": accuracy * 0.8,
            "wrong_answers": [],
            "recommendations": [],
            "concept_weaver": None
        }

    try:
        cleaned_data = clean_json_response(raw_response)
        return json.loads(cleaned_data)
    except Exception as e:
        print(f"JSON Parsing Error in Performance Analysis: {e}")
        # Default fallback
        return {
            "summary": "Great effort! Keep practicing to improve.",
            "accuracy": accuracy,
            "mastery": accuracy * 0.8,
            "wrong_answers": [],
            "recommendations": [],
            "concept_weaver": {
                "foundational_gap": "Concept Basics",
                "bridge_lesson": "Focus on the core fundamentals of this topic first.",
                "why_it_matters": "A strong base leads to faster learning.",
                "youtube_query": topic + " basics"
            }
        }
