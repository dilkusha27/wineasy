from flask import Flask, jsonify, request
import requests
import subprocess
from blueprints.upload import upload_bp
from wineasyOCR import wineasyOCR
from wineasyTEXT import wineasyTEXT
import webbrowser
import os
import time

app = Flask(__name__)
app.register_blueprint(upload_bp)
app.register_blueprint(wineasyOCR)
app.register_blueprint(wineasyTEXT)
    
# 음성 인식 스킬 처리
# Flask 앱 (Flask에서 Streamlit 실행)
@app.route('/api/speech', methods=['POST'])
def handle_stt():

    body = request.get_json()
    print(body)
    print(body['userRequest']['utterance'])

    # voice_assistant.py의 절대 경로
    script_dir = os.path.dirname(os.path.abspath(__file__))  # app.py의 디렉토리 절대 경로
    script_path = os.path.join(script_dir, "voice_assistant.py")

    # Streamlit 로그 파일로 리다이렉트
    process = subprocess.Popen(["streamlit", "run", script_path, "--server.port", "8501"])

    # 브라우저에서 열기
    webbrowser.open("http://localhost:8501")

    responseBody = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "음성 인식을 시작합니다."
                    }
                }
            ]
        }
    }

    return jsonify(responseBody)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


