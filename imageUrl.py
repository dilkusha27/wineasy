from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/imageUrl', methods=['POST'])
def imageUrl():
    data = request.json
    image_url = None

    # Check if 'action' and 'params' exist in the incoming data
    if 'action' in data and 'params' in data['action']:
        params = data['action']['params']
        # Extract 'image_url' from params
        if 'image_url' in params:
            image_url = params['image_url']

    # Create a response based on whether image_url was found
    if image_url:
        response_text = f'이미지 URL: {image_url}'
    else:
        response_text = '이미지가 포함되어 있지 않습니다.'

    # Return the response as JSON
    return jsonify({
        'version': '2.0',
        'template': {
            'outputs': [
                {
                    'simpleText': {
                        'text': response_text
                    }
                }
            ]
        }
    })

if __name__ == '__main__':
    app.run(host='localhost', port=5000)