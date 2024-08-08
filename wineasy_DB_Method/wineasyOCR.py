from flask import Flask, request, jsonify
import requests
import json
import re
from PIL import Image, ImageFilter, UnidentifiedImageError
import io
import logging
import numpy as np
from paddleocr import PaddleOCR
from .db.db import get_wine_detail_by_name  # db 모듈의 함수를 올바르게 임포트합니다
from flask import Blueprint
import os

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# OCR 인스턴스 초기화 (영어와 각도 인식 포함)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# 이미지 전처리 함수: 흑백 변환 및 필터 적용
def preprocess_image(image):
    # 이미지 흑백 변환
    image = image.convert('L')
    # 노이즈 제거를 위해 필터 적용
    image = image.filter(ImageFilter.MedianFilter())
    return image

# 이미지 크기 조정 함수: 높이를 800으로 맞추기
def resize_image(image, target_height=800):
    # 현재 이미지의 너비와 높이 얻기
    width, height = image.size
    # 목표 높이에 맞춰 너비 재계산
    new_height = target_height
    new_width = int((target_height / height) * width)
    # 이미지 크기 조정 및 반환
    return image.resize((new_width, new_height), Image.LANCZOS)

# 이미지에서 텍스트 추출 함수
def extract_text_from_image(image_bytes):
    try:
        # 바이트 데이터를 이미지로 변환
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except UnidentifiedImageError:
        # 이미지 변환 실패 시 None 반환
        return None
    
    # 이미지 전처리
    image = preprocess_image(image)

    # 이미지 크기 조정
    image = resize_image(image)
    
    # 이미지 데이터를 numpy 배열로 변환
    image_np = np.array(image)

    # 전처리된 이미지를 파일로 저장하여 확인
    processed_image_path = 'static/downloads/processed_image.jpg'
    Image.fromarray(image_np).save(processed_image_path)
    logging.debug(f"Processed image saved at '{processed_image_path}'")

    # OCR을 사용하여 텍스트 인식
    result = ocr.ocr(image_np, cls=True)

    # 인식된 텍스트 라인 수집
    text_lines = []
    for line in result:
        for word_info in line:
            _, (text, _) = word_info
            text_lines.append(text)
    
    # 텍스트 라인을 공백으로 구분하여 결합
    return ' '.join(text_lines)

wineasyOCR = Blueprint('wineasyOCR', __name__)

@wineasyOCR.route('/process_image', methods=['POST'])
def process_image():

    # 플러그인이 아니라 일반 엔티티로 받아서 처리하려고 데이터 어떻게 받아오는지 확인하는 과정
    # 데이터를 잘 받아와도 로그는 전혀 표시되지 않음
    """
    logging.info("Entered process_image function")

    raw_data = request.data.decode('utf-8')
    logging.info(f"Received raw data: {raw_data}")
    
    try:
        data = request.get_json()
        logging.info(f"Parsed JSON data: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {str(e)}")
        return jsonify({'error': 'Invalid JSON format'}), 400

    if not data:
        logging.error('No JSON data received')
        return jsonify({'error': 'No JSON data received'}), 400
    """
        
    data = request.get_json()
        
    if 'action' in data and 'params' in data['action']:
        wine_image_data = data['action']['params'].get('wine_image')
        if wine_image_data:
            try:
                # JSON 문자열 파싱
                wine_image_json = json.loads(wine_image_data)
                logging.debug(f"wine_image_json: {wine_image_json}")
                
                # secureUrls에서 URL 추출
                secure_urls = wine_image_json.get('secureUrls')
                image_url_match = re.search(r'http://[^\s)]+', secure_urls)
                if image_url_match:
                    image_url = image_url_match.group(0)
                    
                    # 경로 설정
                    download_folder = 'static/downloads'
                    os.makedirs(download_folder, exist_ok=True)  # 폴더가 존재하지 않으면 생성

                    # 이미지 다운로드 및 처리
                    response = requests.get(image_url)
                    image_bytes = response.content
                    
                    """
                    image_path = os.path.join(download_folder, 'downloaded_image.jpg')
                    logging.debug("Image downloaded successfully")

                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)
                    logging.debug(f"Image saved at '{image_path}'")              
                    """
                    
                    # 이미지에서 텍스트 추출
                    text_from_image = extract_text_from_image(image_bytes)
                    logging.debug(f"Extracted text from image: {text_from_image}")
                    
                    if not text_from_image:
                        return jsonify({'error': 'No text detected'}), 400
                    
                    # 검출된 텍스트를 사용해 와인 정보 조회
                    wine_details = get_wine_detail_by_name(text_from_image)
                    logging.debug(f"Retrieved wine details: {wine_details}")
                    
                    if wine_details:
                        wine = wine_details[0]
                        wine_type = wine['wine_type']
                        # 와인 타입에 따른 이모지 선택
                        wine_emoji = {
                            "레드": "🍷",
                            "화이트": "🥂",
                            "스파클링": "🍾"
                        }.get(wine_type, "🍷")  # 기본값은 레드 와인 이모지
                        
                        numbered_food_list = '\n'.join([f"{i+1}. {food.strip()}" for i, food in enumerate(wine['recommended_dish'].split(','))])
                        
                        skill_text = (
                            f"{wine_emoji} {wine['wine_name_ko']} {wine_emoji}\n"
                            f"({wine['wine_name_en']})\n\n"
                            "📝 테이스팅 노트\n\n"
                            f"\"{wine['taste']}\"\n\n"
                            "🍽 페어링하기 좋은 음식 Top 3\n\n"
                            f"{numbered_food_list}\n\n"
                            "추천이 도움이 되셨을까요?\n"
                            "페어링 추천이 필요한\n"
                            f"{wine_emoji}다른 와인{wine_emoji}이 있으시다면\n"
                            "편하게 말씀해주세요! 😆"
                        )
                    else:
                        skill_text = "해당 와인 정보를 찾을 수 없습니다."

                    # OCR 결과를 서버 로그에 기록
                    logging.info(f"OCR 결과: {text_from_image}")

                    # 결과 반환
                    return jsonify({
                        'version': "2.0",
                        'template': {
                            'outputs': [
                                {
                                    'simpleText': {
                                        'text': skill_text
                                    }
                                }
                            ]
                        }
                    })
                else:
                    return jsonify({'error': 'Invalid image URL format'})
            except Exception as e:
                logging.error(f"Error processing image: {str(e)}")
                return jsonify({'error': str(e)})
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5000)