from flask import Flask
from wineasy_DB_Method.wineasyOCR import wineasyOCR
from wineasy_DB_Method.wineasyTEXT import wineasyTEXT

app = Flask(__name__)

# 블루프린트 등록
app.register_blueprint(wineasyOCR)
app.register_blueprint(wineasyTEXT)

if __name__ == '__main__':
    app.run(port=5000)