import os
import json
import requests
from flask import Flask, request, jsonify

from unpack import get_value

'''
Flask app that takes in zipped 3d model file, JSON data, and Sketchfab API token
and publishes to Sketchfab. 

Returns JSON object with two fields, if successful, indicating Sketchfab UID and 
permalink to hosted model location. 

JSON data can be arbitrary: needs at least a 'name' field for the title of the 
published model. Everything else can get dumped into a 'description' field. 

'''

app = Flask(__name__) 

@app.route('/models', methods=['POST', 'GET', 'DELETE'])
def models():
    #Posts models to sketchfab.
    if request.method == 'POST':
        SKETCHFAB_DOMAIN = 'sketchfab.com'
        SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
        MODEL_ENDPOINT = SKETCHFAB_API_URL + '/models'
        
        token = get_value(request, 'config', 'token')
        headers = {'Authorization': 'Token {}'.format(token)}
        name = get_value(request, 'data', 'name')
        data = {'name': name}
        
        # data = {'name': post_data.get('name'),
        #         'description': post_data.get('description'),
        #         'tags': post_data.get('tags'),
        #         'categories': post_data.get('categories'),
        #         'license': post_data.get('license')}

        file = request.files['file']
        file.save('model.zip')
        f = open('model.zip', 'rb')
        files = {'modelFile': f}


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




    if request.method == 'DELETE':
        try:
            uid = get_value(request, 'data', 'uid')
            SKETCHFAB_DOMAIN = 'sketchfab.com'
            SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
            
            
            token = get_value(request, 'config', 'token')
            headers = {'Authorization': 'Token {}'.format(token)}
            model_endpoint = SKETCHFAB_API_URL + '/models/{}'.format(uid)


            r = requests.delete(model_endpoint, headers=headers)
            if r.status_code != 204:
                return jsonify({"msg": "model does not exist", "content": str(r.content)})
            else:
                
                return jsonify({"msg": "model successfully deleted", "content": r.status_code})
        except Exception as e:
            return jsonify({'requestException': str(e)})

@app.route('/account', methods=['POST', 'GET', 'DELETE'])
def account():
    #Gets a published list of models from sketchfab account.
    if request.method == 'GET':
        SKETCHFAB_DOMAIN = 'sketchfab.com'
        SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
        MODEL_ENDPOINT = SKETCHFAB_API_URL + '/me/models'
        
        token = get_value(request, 'config', 'token')
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
