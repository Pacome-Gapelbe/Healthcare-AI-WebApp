from flask import Blueprint, render_template, request, jsonify
import requests
from flask_login import login_required

views = Blueprint('views', __name__)
GEMINI_API_KEY = "AIzaSyCHD5ngEnf7_SbHhkwgDaOdTODIIN02jvM"

@views.route("/")
# @login_required
def home():
    return render_template('base.html')

@views.route("/kidney")
@login_required
def kidney():
    return render_template('kidney_index.html')

@views.route("/kidney_form")
@login_required
def kidney_form():
    return render_template('kidney.html')

@views.route("/liver")
@login_required
def liver():
    return render_template('liver_index.html')

@views.route("/liver_form")
@login_required
def liver_form():
    return render_template('liver.html')

@views.route("/heart")
@login_required
def heart():
    return render_template('heart_index.html')

@views.route("/heart_form")
@login_required
def heart_form():
    return render_template('heart.html')

@views.route("/stroke")
@login_required
def stroke():
    return render_template('stroke_index.html')

@views.route("/stroke_form")
@login_required
def stroke_form():
    return render_template('stroke.html')

@views.route("/diabete")
@login_required
def diabete():
    return render_template('diabete_index.html')

@views.route("/diabete_form")
@login_required
def diabete_form():
    return render_template('diabete.html')

@views.route("/pneumonia")
@login_required
def pneumonia():
    return render_template('pneumonia_index.html')

@views.route("/pneumonia_form")
@login_required
def pneumonia_form():
    return render_template('pneumonia.html')

@views.route("/chat_page", methods=["GET", "POST"])
@login_required
def chat_page():
    if request.method == "GET":
        return render_template('chat.html')
    elif request.method == "POST":
        user_input = request.json.get("message")
        prompt = f"You are a helpful health assistant. Answer health-related questions clearly. If the question is not health-related, politely decline.\n\nUser: {user_input}\nAssistant:"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
       
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            try:
                assistant_reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                assistant_reply = "Sorry, I couldn't understand the response."
        else:
            assistant_reply = f"Error {response.status_code}: {response.text}"
        
        return jsonify({"reply": assistant_reply})
