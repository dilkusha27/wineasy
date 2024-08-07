from flask import Blueprint, request, jsonify
from PIL import Image, ImageFilter, UnidentifiedImageError
from paddleocr import PaddleOCR
import numpy as np
import io
import db

# Flask Blueprint 생성
upload_bp = Blueprint('upload', __name__)

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

# 이미지 업로드 엔드포인트 정의
@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        # GET 요청 시 안내 메시지 반환
        return "Please use POST method to upload an image."

    try:
        # 클라이언트로부터 업로드된 이미지 파일 가져오기
        file = request.files.get('image')
        if not file:
            # 파일이 없을 경우 오류 메시지 반환
            return jsonify({'error': 'No file provided'}), 400
        
        # 파일 데이터를 읽어와서 텍스트 추출
        image_bytes = file.read()
        text = extract_text_from_image(image_bytes)
        
        if not text:
            # 텍스트가 검출되지 않은 경우 오류 메시지 반환
            return jsonify({'error': 'No text detected'}), 400
        
        # 검출된 텍스트를 사용해 와인 정보 조회
        wine_info = db.get_wine_info_by_name(text)
        # 추출된 텍스트와 와인 정보를 JSON 응답으로 반환
        return jsonify({'text': text, 'wine_info': wine_info})
    except Exception as e:
        # 예외 발생 시 로그 기록 및 오류 메시지 반환
        upload_bp.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request.'}), 500

# 웹훅 엔드포인트 정의
@upload_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # GET 요청 시 안내 메시지 반환
        return "Webhook endpoint is active. Please use POST method to send data."

    if request.method == 'POST':
        try:
            # 클라이언트로부터 JSON 데이터 수신
            data = request.json
            if not data:
                # 데이터가 없을 경우 오류 메시지 반환
                return jsonify({'error': 'No data provided'}), 400

            # 이벤트 타입 확인
            event_type = data.get('event_type')
            if event_type == 'wine_info_request':
                # 이벤트 타입이 'wine_info_request'인 경우
                wine_name = data.get('wine_name')
                if wine_name:
                    # 와인 이름으로 와인 정보 조회 및 반환
                    wine_info = db.get_wine_info_by_name(wine_name)
                    return jsonify({'wine_info': wine_info})
                else:
                    # 와인 이름이 제공되지 않은 경우 오류 메시지 반환
                    return jsonify({'error': 'wine_name not provided'}), 400

            # 성공적으로 처리된 경우 상태 반환
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            # 예외 발생 시 로그 기록 및 오류 메시지 반환
            upload_bp.logger.error(f"Error processing webhook: {e}")
            return jsonify({'error': 'Webhook processing failed'}), 500
