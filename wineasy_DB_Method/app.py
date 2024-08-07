from flask import Flask, jsonify
from blueprints.upload import upload_bp

app = Flask(__name__)
app.register_blueprint(upload_bp)

@app.route('/')
def home():
    return "Welcome to the Wine Label OCR API. Use /upload to upload an image or /webhook for webhook events."

if __name__ == '__main__':
    app.run(debug=True)
