from flask import Flask, request, jsonify
import requests
from google.cloud import vision

app = Flask(__name__)
vision_client = vision.ImageAnnotatorClient()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'image' in data['userRequest']['attachment']:
        image_url = data['userRequest']['attachment']['image']['url']
        wine_name = process_image(image_url)
    else:
        wine_name = data['userRequest']['utterance']
    
    wine_info = get_wine_info(wine_name)
    response_text = generate_response(wine_info)
    return jsonify({"version": "2.0", "template": {"outputs": [{"simpleText": {"text": response_text}}]}})

def process_image(image_url):
    response = requests.get(image_url)
    image = vision.Image(content=response.content)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description.strip() if texts else "와인 이름을 인식할 수 없습니다."

def get_wine_info(wine_name):
    # 여기에 데이터베이스 조회 로직 추가
    # 예시 데이터
    wine_info = {
        "kor_name": "클라우디 베이, 소비뇽 블랑",
        "eng_name": "Cloudy Bay, Sauvignon Blanc",
        "tasting_note": "엷은 초록색과 노랑색을 띠고 신선한 열대 과일과 라임향과 풋풋한 풀내음이 느껴진다. 입안에서는 산뜻한 느낌을 느낄 수 있으며 여운이 깔끔하게 떨어지는 와인이다.",
        "food_pairing": ["해산물요리", "카레", "치즈"]
    }
    return wine_info

def generate_response(wine_info):
    response_text = f"""
    🍷 {wine_info['kor_name']}
    ({wine_info['eng_name']})

    📝 테이스팅 노트
    "{wine_info['tasting_note']}"

    🍽 페어링하기 좋은 음식 Top 3
    {', '.join(wine_info['food_pairing'])}
    """
    return response_text.strip()

if __name__ == '__main__':
    app.run(debug=True)