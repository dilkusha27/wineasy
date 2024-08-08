from flask import Flask
from wineasy_DB_Method.wineasyOCR2 import wineasyOCR2
from wineasy_DB_Method.wineasyTEXT import wineasyTEXT

app = Flask(__name__)

# 블루프린트 등록
app.register_blueprint(wineasyOCR2)
app.register_blueprint(wineasyTEXT)

if __name__ == '__main__':
    app.run(port=5000)