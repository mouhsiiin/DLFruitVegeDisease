from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from PIL import Image
from io import BytesIO
import numpy as np

# Import the prediction module
from predict import FruitsVeggiesHealthClassifier

# Initialize the classifier (ensure model path is correct)
classifier = FruitsVeggiesHealthClassifier('cnn_model.keras')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/')
def home():
    return "Fruits & Vegetables Health Classifier API"




@app.route('/predict', methods=['POST'])
def predict_image():
    """
    Predict health status of a fruit or vegetable from an image.
    Accepts image upload or image URL.
    """
    try:
        # Check if image is uploaded via file
        if 'image' in request.files:
            image_file = request.files['image']
            img = Image.open(image_file)
        
        # Check if image URL is provided
        elif 'image_url' in request.json:
            url = request.json['image_url']
            response = requests.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        
        else:
            return jsonify({
                'error': 'No image provided. Upload an image or provide an image URL.'
            }), 400

        # Perform prediction
        prediction = classifier.predict(img)
        
        return jsonify({
            'prediction': prediction['class'],
            'confidence': prediction['confidence']
        })

    except requests.exceptions.RequestException:
        return jsonify({'error': 'Invalid image URL'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)