
from flask import Blueprint, render_template, request, jsonify
import requests

# Create Blueprint
views = Blueprint('views', __name__)
GEMINI_API_KEY = "AIzaSyCHD5ngEnf7_SbHhkwgDaOdTODIIN02jvM"
# Home route
@views.route("/")
def home():
    return render_template('base.html')

# Kidney routes
@views.route("/kidney")
def kidney():
    return render_template('kidney_index.html')

@views.route("/kidney_form")
def kidney_form():
    return render_template('kidney.html')

# Liver routes
@views.route("/liver")
def liver():
    return render_template('liver_index.html')

@views.route("/liver_form")
def liver_form():
    return render_template('liver.html')

# Heart routes
@views.route("/heart")
def heart():
    return render_template('heart_index.html')

@views.route("/heart_form")
def heart_form():
    return render_template('heart.html')

# Stroke routes
@views.route("/stroke")
def stroke():
    return render_template('stroke_index.html')

@views.route("/stroke_form")
def stroke_form():
    return render_template('stroke.html')

# Diabetes routes
@views.route("/diabete")
def diabete():
    return render_template('diabete_index.html')

@views.route("/diabete_form")
def diabete_form():
    return render_template('diabete.html')

# Pneumonia routes
@views.route("/pneumonia")
def pneumonia():
    return render_template('pneumonia_index.html')

@views.route("/pneumonia_form")
def pneumonia_form():
    return render_template('pneumonia.html')

# Chatbot page route
@views.route("/chat_page", methods=["GET", "POST"])
def chat_page():
    if request.method == "GET":
        return render_template('chat.html')
    elif request.method == "POST":
        user_input = request.json.get("message")
        # Define the instruction prompt
        prompt = f"You are a helpful health assistant. Answer health-related questions clearly. If the question is not health-related, politely decline.\n\nUser: {user_input}\nAssistant:"
        
        # Prepare the request for Gemini 2.0 Flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
       
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make the API call
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            try:
                assistant_reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                assistant_reply = "Sorry, I couldn't understand the response."
        else:
            assistant_reply = f"Error {response.status_code}: {response.text}"
        
        return jsonify({"reply": assistant_reply})