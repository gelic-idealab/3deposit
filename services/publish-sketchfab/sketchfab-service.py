import os
import json
import requests
from flask import Flask, request, jsonify
import logging
from unpack_001 import get_value

'''
Flask app that takes in zipped 3d model file, JSON data, and Sketchfab API
token and publishes to Sketchfab.

Returns JSON object with two fields, if successful, indicating Sketchfab UID
and permalink to hosted model location.

JSON data can be arbitrary: needs at least a 'name' field for the title of the
published model. Everything else can get dumped into a 'description' field.

'''

app = Flask(__name__) 


@app.route('/models', methods=['POST', 'GET', 'DELETE'])
def models():
    try:
        # Posts the model to sketchfab.
        if request.method == 'POST':
            logging.debug(msg='sketchfab req: {}'.format(request.form))

            SKETCHFAB_DOMAIN = 'sketchfab.com'
            SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
            MODEL_ENDPOINT = SKETCHFAB_API_URL + '/models'

            logging.debug(msg='sketchfab req: {}'.format(request.form))
            # token = get_value(request, 'config', 'token')
            config = json.loads(request.form.get('config'))
            auth = config.get('auth')
            token = auth.get('token')
            headers = {'Authorization': 'Token {}'.format(token)}
            # name = get_value(request, 'data', 'Creator Name')
            data = json.loads(request.form.get('data'))
            metadata = data.get('metadata')
            name = metadata.get('Object Title')
            logging.debug(msg='sketchfab name: {}'.format(name))
            data = {'name': name}
            logging.debug('sketchfab values: {}, {}'.format(token, name))

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
                uid = response.get('uid')
                if os.path.exists('model.zip'):
                    os.remove('model.zip')
                return jsonify({"resource_id": uid, "location": f"https://sketchfab.com/models/{uid}/embed"})

        # Deletes the model from sketchfab.
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
                    return jsonify({"msg": "Model does not exist.", "content": str(r.content)})
                else:
                    return jsonify({"msg": "Model successfully deleted.", "content": r.status_code})
            except Exception as e:
                return jsonify({'requestException': str(e)})
    except Exception as err:
        return jsonify({'err': str(err)})

    # Returns the details of the model.
    if request.method == 'GET':
        try:
            data = json.loads(request.form.get('data'))

            uid = data.get('resource_id')
            SKETCHFAB_DOMAIN = 'sketchfab.com'
            SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)

            config = json.loads(request.form.get('config'))
            auth = config.get('auth')
            token = auth.get('token')

            headers = {'Authorization': 'Token {}'.format(token)}
            model_endpoint = SKETCHFAB_API_URL + '/models/{}'.format(uid)

            r = requests.get(model_endpoint, headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'requestException': e})
        else:
            response = r.json()
            return jsonify(response)


@app.route('/users', methods=['POST', 'GET', 'DELETE'])
def users():
    # Get the user information
    if request.method == 'GET':
        try:
            uid = get_value(request, 'data', 'resource_id')
            SKETCHFAB_DOMAIN = 'sketchfab.com'
            SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)

            token = get_value(request, 'config', 'token')
            headers = {'Authorization': 'Token {}'.format(token)}
            users_endpoint = SKETCHFAB_API_URL + '/users/{}'.format(uid)

            r = requests.get(users_endpoint, headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'requestException': e})
        else:
            response = r.json()
            return jsonify(response)


if __name__ == '__main__':
    app.run()
