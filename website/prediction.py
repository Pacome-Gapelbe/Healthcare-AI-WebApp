from flask import Blueprint, render_template, request, send_from_directory, make_response
from flask_login import current_user, login_required
from .app_functions import ValuePredictor, pred
from . import db
from .models import Prediction
import os
import json
from werkzeug.utils import secure_filename
import requests
import pandas as pd
from io import BytesIO


prediction = Blueprint('prediction', __name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

dir_path = os.path.dirname(os.path.realpath(__file__))

GEMINI_API_KEY = os.getenv("Gemini_key")


def reword_message(original_message):
    """Reword medical predictions to be compassionate and non-alarming for patients."""
    try:
        prompt = f"""You are a compassionate medical communication assistant. Reword the following medical prediction gently and supportively, without causing alarm or fear. 

Rules:
- If negative/concerning, soften it, suggest consulting a doctor, emphasize it's only a prediction, and offer reassurance.
- If positive/good, provide encouragement and positivity.
- Use simple language, no medical jargon.
- Always recommend professional medical advice.
- Be concise and warm.

IMPORTANT: Do NOT include any introductory phrases, explanations, or apologies. 
Only output the reworded message text exactly.

Original message: {original_message}

Reworded message:"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 150,
                "topP": 0.9,
                "topK": 20
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                response_data = response.json()
                reworded_message = response_data["candidates"][0]["content"]["parts"][0]["text"]
                # Strip to remove leading/trailing whitespace only
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
        to_predict_dict = request.form.to_dict()
        try:
            # Convert all input values to float
            to_predict_list = [float(value) for value in to_predict_dict.values()]
        except ValueError:
            # Handle the case where conversion fails
            return "Invalid input values. Please enter valid numbers.", 400

        # Run prediction model
        result, disease = ValuePredictor(to_predict_list)

        # Create the original prediction message
        if result == 0:
            original_message = f"No need to worry. You have no symptoms of {disease} disease."
        else:
            original_message = f"It looks like you may be at risk for {disease} disease. Please consult a medical professional."

        # Call Gemini API to get the reworded message
        reworded_message = reword_message(original_message)

        # Prepare input_data as JSON string to save in DB
        input_data_json = json.dumps(to_predict_dict)

        # Get current user or fallback to anonymous
        user_id = current_user.username if current_user.is_authenticated else "Anonymous"

        # Save prediction to DB
        new_prediction = Prediction(
            disease_type=disease,
            input_data=input_data_json,
            prediction_result=result,
            original_message=original_message,
            reworded_message=reworded_message,
            user_identifier=user_id
        )
        db.session.add(new_prediction)
        db.session.commit()

        # Render result page
        return render_template(
            "result.html",
            prediction=result,
            page=disease,
            improved_message=reworded_message
        )
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


@prediction.route('/predictions')
@login_required  # ensure only logged-in users can access
def show_predictions():
    all_predictions = Prediction.query.filter_by(user_identifier=current_user.username).order_by(Prediction.date.desc()).all()

    import json
    for pred in all_predictions:
        try:
            pred.input_data = json.dumps(json.loads(pred.input_data), indent=2)
        except Exception:
            pass

    return render_template('predictions_list.html', predictions=all_predictions)


@prediction.route('/export_predictions')
@login_required
def export_predictions():
    # Get the predictions data
    all_predictions = Prediction.query.filter_by(user_identifier=current_user.username).order_by(Prediction.date.desc()).all()
    
    # Convert to pandas DataFrame
    data = []
    for pred in all_predictions:
        data.append({
            'ID': pred.id,
            'Date': pred.date.strftime('%Y-%m-%d %H:%M:%S'),
            'Disease Type': pred.disease_type,
            'Input Data': pred.input_data,
            'Prediction Result': pred.prediction_result,
            'Original Message': pred.original_message,
            'Reworded Message': pred.reworded_message,
            'User': pred.user_identifier or 'Anonymous'
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, sheet_name='Predictions', index=False)
    writer.close()
    output.seek(0)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=predictions.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response

