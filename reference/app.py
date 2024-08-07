from flask import Flask, request
from KakaoTemplate import KakaoTemplate

# Flask 어플리케이션
app = Flask(__name__)

@app.route('/query/test', methods=['POST'])
def query():
    body = request.get_json()
    # 카카오톡 스킬 처리
    body = request.get_json()
    utterance = body['userRequest']['utterance']
    ret = get_answer_from_engine(bottype=bot_type, query=utterance)

    from KakaoTemplate import KakaoTemplate
    skillTemplate = KakaoTemplate()
    return skillTemplate.send_response(ret)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
