from flask import Blueprint, request, jsonify, current_app
from PIL import Image, ImageFilter, UnidentifiedImageError
from paddleocr import PaddleOCR
import numpy as np
import io
from db import db

upload_bp = Blueprint('upload', __name__)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

def preprocess_image(image):
    image = image.convert('L')  # 그레이스케일 변환
    image = image.filter(ImageFilter.MedianFilter())  # 노이즈 제거
    return image

def resize_image(image, target_height=800):
    width, height = image.size
    new_height = target_height
    new_width = int((target_height / height) * width)
    return image.resize((new_width, new_height), Image.LANCZOS)

def extract_text_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except UnidentifiedImageError:
        return None
    
    image = preprocess_image(image)
    image = resize_image(image)
    image_np = np.array(image)
    result = ocr.ocr(image_np, cls=True)

    text_lines = []
    for line in result:
        for word_info in line:
            _, (text, _) = word_info
            text_lines.append(text)
    
    return ' '.join(text_lines)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return "Please use POST method to upload an image."

    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        image_bytes = file.read()
        text = extract_text_from_image(image_bytes)
        
        if not text:
            return jsonify({'error': 'No text detected'}), 400
        
        wine_info = db.get_wine_info_by_name(text)
        return jsonify({'text': text, 'wine_info': wine_info})
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

@upload_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return "Webhook endpoint is active. Please use POST method to send data."

    if request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            event_type = data.get('event_type')
            if event_type == 'wine_info_request':
                wine_name = data.get('wine_name')
                if wine_name:
                    wine_info = db.get_wine_info_by_name(wine_name)
                    return jsonify({'wine_info': wine_info})
                else:
                    return jsonify({'error': 'wine_name not provided'}), 400

            return jsonify({'status': 'success'}), 200
        except Exception as e:
            current_app.logger.error(f"Error processing webhook: {e}")
            return jsonify({'error': 'Webhook processing failed'}), 500
