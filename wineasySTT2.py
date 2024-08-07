from flask import Flask, render_template, request, jsonify
from gtts import gTTS
import os
import speech_recognition as sr
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 설정 추가

# STT 함수
@app.route('/stt', methods=['POST'])
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="ko-KR")
            return jsonify({'text': text})
        except sr.UnknownValueError:
            return jsonify({'error': 'Google Speech Recognition could not understand audio'})
        except sr.RequestError as e:
            return jsonify({'error': f'Could not request results from Google Speech Recognition service; {e}'})

# TTS 함수
@app.route('/tts', methods=['POST'])
def text_to_speech():
    text = request.form['text']
    tts = gTTS(text=text, lang='ko')
    tts.save("output.mp3")
    return jsonify({'audio': 'output.mp3'})

@app.route('/speech', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=8080)