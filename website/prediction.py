

from flask import Blueprint, render_template, request, send_from_directory
from .app_functions import ValuePredictor, pred
import os
from werkzeug.utils import secure_filename
import requests

prediction = Blueprint('prediction', __name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

dir_path = os.path.dirname(os.path.realpath(__file__))

GEMINI_API_KEY = "AIzaSyCHD5ngEnf7_SbHhkwgDaOdTODIIN02jvM"
def reword_message(original_message):
    """Reword medical predictions to be compassionate and non-alarming for patients."""
    try:
        # Create a specific prompt for medical prediction rewording
        prompt = f"""You are a compassionate medical communication assistant. Your job is to reword medical predictions in a gentle, supportive way that doesn't cause fear or panic in patients.

Rules:
- If the prediction is negative/concerning: Make it gentle, suggest consulting a doctor, emphasize it's just a prediction, offer reassurance
- If the prediction is positive/good: Provide encouragement and positive reinforcement
- Keep responses concise and caring
- Always recommend professional medical consultation
- Avoid medical jargon
- Be warm and supportive

Original message: {original_message}

Reworded message:"""
        
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
            ],
            "generationConfig": {
                "temperature": 0.3,  # Lower temperature for more consistent, gentle responses
                "maxOutputTokens": 150,  # Shorter, concise responses
                "topP": 0.9,
                "topK": 20
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make the API call
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                reworded_message = response_data["candidates"][0]["content"]["parts"][0]["text"]
                return reworded_message.strip()
            except (KeyError, IndexError) as e:
                print("Gemini Response Error:", e)
                return original_message
        else:
            print(f"Gemini API Error {response.status_code}:", response.text)
            return original_message
            
    except Exception as e:
        print("Error:", e)
        return original_message

@prediction.route('/predict', methods=["POST", "GET"])
def predict():
    if request.method == "POST":
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        to_predict_list = list(map(float, to_predict_list))
        result, page = ValuePredictor(to_predict_list)

        if result == 0:
            original_message = f"No need to worry. You have no symptoms of {page} disease."
        else:
            original_message = f"It looks like you may be at risk for {page} disease. Please consult a medical professional."

        reworded_message = reword_message(original_message)

        print(f"Prediction: {result}, Page: {page}, Message: {reworded_message}")  # ✅ Debugging

        return render_template("result.html", prediction=result, page=page, improved_message=reworded_message)

    else:
        return render_template('base.html')


@prediction.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == "GET":
        return render_template('pneumonia.html', title='Pneumonia Disease')
    else:
        file = request.files["file"]
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(file.filename))
        file.save(file_path)
        indices = {0: 'Normal', 1: 'Pneumonia'}
        result = pred(file_path)

        if result > 0.5:
            label = indices[1]
            accuracy = result * 100
        else:
            label = indices[0]
            accuracy = 100 - result

        return render_template('deep_pred.html', image_file_name=file.filename, label=label, accuracy=accuracy)


@prediction.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)








