import os
import json
import requests
from flask import Flask, request, jsonify

'''
Flask app that takes in zipped 3d model file, JSON data, and Sketchfab API token
and publishes to Sketchfab. 

Returns JSON object with two fields, if successful, indicating Sketchfab UID and 
permalink to hosted model location. 

JSON data can be arbitrary: needs at least a 'name' field for the title of the 
published model. Everything else can get dumped into a 'description' field. 

'''

app = Flask(__name__)

@app.route('/v3/account/models', methods=['POST', 'GET'])
def models():
    #Posts models to sketchfab.
    if request.method == 'POST':
        SKETCHFAB_DOMAIN = 'sketchfab.com'
        SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
        MODEL_ENDPOINT = SKETCHFAB_API_URL + '/models'
        
        post_data = json.loads(request.form.get('data'))
        token = post_data.get('token')
        headers = {'Authorization': 'Token {}'.format(token)}
        
        data = {'name': post_data.get('name'),
                'description': post_data.get('description'),
                'tags': post_data.get('tags'),
                'categories': post_data.get('categories'),
                'license': post_data.get('license'),
                'private': post_data.get('private'),
                'password': post_data.get('password'),
                'isPublished': post_data.get('isPublished'),
                'isInspectable': post_data.get('isInspectable')}

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

def account():
    #Gets a published list of models from sketchfab account
    if request.method == 'GET':
        SKETCHFAB_DOMAIN = 'sketchfab.com'
        SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
        MODEL_ENDPOINT = SKETCHFAB_API_URL + '/me/models'
        
        config = json.loads(request.form.get('config'))
        auth = config.get('auth')
        token = auth.get('token')
        headers = {'Authorization': 'Token {}'.format(token)}

        try:
            r = requests.get(MODEL_ENDPOINT, headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'requestException': e})
        else:
            response = r.json()
            print(response)
            return jsonify(response)
        

if __name__ == '__main__':
    app.run()
