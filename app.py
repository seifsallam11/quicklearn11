# app.py

from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
import re

# -----------------------------
# تحميل متغيرات البيئة مباشرة من إعدادات PythonAnywhere
# -----------------------------
SITE_URL = os.getenv("SITE_URL", "/")

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.context_processor
def inject_site_url():
    return dict(SITE_URL=SITE_URL)

# -----------------------------
# إعداد Gemini API
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # هذا الخطأ سيظهر إذا لم تقم بإعداد المفتاح في صفحة Web
    raise ValueError("No GEMINI_API_KEY found. Make sure it's set in the web app settings.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-pro")

# -----------------------------
# البرومبت
# -----------------------------
PROMPT = """
You are an assistant specialized in visual lesson summarization.
Your task: transform any lesson into a clean HTML summary based on symbols, easy to read and memorize, as if you are the one summarizing and creatively presenting it.


---

Phase 1 — Content Cleaning

Extract only the core ideas (concepts, laws, formulas, facts).
Remove filler, background, and repeated information.


---

Phase 2 — Content Segmentation

Divide the content into roughly equal blocks.
Each block = a main topic or a group of related concepts.
Within each block: one line = one idea.


---

Phase 3 — Creative Symbolic Expression

Keep only symbolic words, making each line concise, clear, and creative, as if you are the summarizer.
Use Google Fonts Material Icons instead of connectors or to illustrate relationships (e.g., use a plus symbol instead of "and", arrows for relationships, icons representing logical values instead of linking words).
Do not use emojis or icons outside the Google Fonts icons library.


---

Phase 4 — Add Icons to Each Idea

Add one suitable icon per line, clear and expressive.
Use only icons from the Google Fonts Material Icons library.


---

Phase 5 — Word Coloring

Color each word according to what it represents.
Words that cannot be assigned a specific color should be black.
Colors should be bright and prominent.
Ensure each word keeps the same color every time it appears.


---

Phase 6 — HTML Output

The output = a single clean HTML file.
Each block = <div>
Each line = <p>

Structure:

Language = same as the lesson language

Font:

English → Roboto Slab

Arabic → Beiruti




---

Phase 7 — Formatting

Summary should be clean, simple, and easy to read.
Icons may be colored if possible.
Words should be clearly separated.
Creativity is allowed, especially in Phase 3, while retaining the core content and relying on logical icons for clarity and understanding.

 so important:
    Return HTML snippet only (no <html>, <head>, <body> tags). Ensure each line is a <p> inside a <div> block.
Use consistent colors for repeated words.
"""

# -----------------------------
# دوال المساعدة
# -----------------------------
def validate_input(text):
    """Validate user input to prevent abuse"""
    if not text or len(text.strip()) < 10:
        return False, "Input too short"
    
    if len(text) > 16000:
        return False, "Input too long"
    
    # Check for excessive special characters (potential spam)
    if re.search(r'[^\w\s.,!?;:@#$%^&*()\-+=\\/\\[\\]{}|<>]', text):
        return False, "Invalid characters detected"
    
    return True, "Valid"

def generate_summary(user_text):
    full_prompt = f"{PROMPT}\n\nLesson Content:\n{user_text}"
    response = model.generate_content(full_prompt)
    return response.text

def list_available_models():
    models = genai.list_models()
    print("Available Models:")
    for m in models:
        print(m.name)

# -----------------------------
# الراوت الرئيسي
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        lesson_text = request.form.get("lesson_text", "").strip()
        
        # Input validation
        is_valid, message = validate_input(lesson_text)
        if not is_valid:
            return f"<div style='padding: 20px; color: #D32F2F; font-family: sans-serif;'><h3>Validation Error</h3><p>{message}</p></div>", 400

        try:
            summary = generate_summary(lesson_text)
            # أرسل الاستجابة بصيغة HTML مباشرة
            return summary
        except Exception as e:
            # أرسل استجابة HTML للخطأ
            return f"<html><body><p>Error: {str(e)}</p></body></html>", 500

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)