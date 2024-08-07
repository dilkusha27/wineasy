from flask import Flask, request, jsonify
from google.cloud import speech
import os

app = Flask(__name__)

# 구글 클라우드 인증 키 파일 경로 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "E:/workplace/wineasy/wineasy-ad30fb0a8127.json"
print(f"Google Cloud Credentials: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")  # 인증 키 파일 경로 로그 출력

# 음성 인식 클라이언트 초기화
speech_client = speech.SpeechClient()

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        print("Received request")  # 요청 수신 로그

        # 요청에서 'wine_name_STT' 파일 파라미터를 확인
        if 'wine_name_STT' not in request.files:
            print("No wine_name_STT in request")  # wine_name_STT 파라미터 없음 로그
            # 'wine_name_STT' 파라미터가 없으면 오류 응답 반환
            return jsonify({"error": "wine_name_STT 파라미터가 필요합니다."}), 400
        
        # 'wine_name_STT' 파라미터에서 파일 가져오기
        audio_file = request.files['wine_name_STT']
        print(f"Received audio file: {audio_file.filename}")  # 받은 파일 로그

        audio_content = audio_file.read()  # 파일 내용을 읽어오기
        print("Read audio content")  # 파일 내용 읽기 로그

        # 음성 파일 내용을 텍스트로 변환
        transcribed_text = transcribe_audio(audio_content)
        print(f"Transcribed text: {transcribed_text}")  # 변환된 텍스트 로그

        if transcribed_text:
            # 변환된 텍스트를 로그에 출력
            print(f"Transcription successful: {transcribed_text}")
            # 성공 응답 반환
            return jsonify({"message": "음성 인식 성공", "transcribed_text": transcribed_text})
        else:
            # 변환 실패 시 오류 응답 반환
            print("Transcription failed")  # 변환 실패 로그
            return jsonify({"error": "음성 파일에서 텍스트를 추출할 수 없습니다."}), 500
    
    except Exception as e:
        # 예외 발생 시 에러 로그 출력 및 오류 응답 반환
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

def transcribe_audio(audio_content):
    """음성 파일에서 텍스트 추출"""
    try:
        print("Starting transcription")  # 변환 시작 로그

        # RecognitionAudio 객체 생성 (음성 데이터 포함)
        audio = speech.RecognitionAudio(content=audio_content)
        print("Created RecognitionAudio object")  # RecognitionAudio 객체 생성 로그

        # RecognitionConfig 객체 생성 (인식 설정 포함)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # 음성 파일의 인코딩 형식
            sample_rate_hertz=16000,  # 샘플링 속도 (Hz)
            language_code='ko-KR'  # 언어 코드 (한국어)
        )
        print("Created RecognitionConfig object")  # RecognitionConfig 객체 생성 로그

        # 구글 STT API 호출하여 음성 인식 요청
        response = speech_client.recognize(config=config, audio=audio)
        print("Received response from Google STT API")  # 구글 STT API 응답 수신 로그

        # 인식 결과 반환 (결과가 있으면 텍스트 반환, 없으면 None 반환)
        if response.results:
            transcript = response.results[0].alternatives[0].transcript.strip()
            print(f"Transcription result: {transcript}")  # 변환 결과 로그
            return transcript
        else:
            print("No transcription results")  # 변환 결과 없음 로그
            return None
    except Exception as e:
        print(f"Error during transcription: {e}")  # 변환 중 오류 로그
        return None

if __name__ == '__main__':
    print("Starting Flask server")  # 서버 시작 로그
    app.run(port=8080)  # Flask 서버 실행 (포트 8080)