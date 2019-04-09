import os
import json
import requests
from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/publish', methods=['POST'])
def publish():

    SKETCHFAB_DOMAIN = 'sketchfab.com'
    SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
    MODEL_ENDPOINT = SKETCHFAB_API_URL + '/models'
    TOKEN = request.form.get('token')

    headers = {'Authorization': 'Token {}'.format(TOKEN)}

    post_data = json.loads(request.form.get('data'))
    data = {'name': post_data.get('name')}

    file = request.files['file']
    file.save('model.zip')
    f = open('model.zip', 'rb')
    files = {'modelFile': f}

    # upload to Sketchfab
    try:
        r = requests.post(MODEL_ENDPOINT, data=data, files=files, headers=headers)
        f.close()
    except requests.exceptions.RequestException as e:
        return jsonify({'requestException': e})
    else:
        response = r.json()
        print(response)
        if os.path.exists('model.zip'):
            os.remove('model.zip')
        return jsonify(response)

if __name__ == '__main__':
    app.run()