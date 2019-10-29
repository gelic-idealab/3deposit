import os
import json
import requests
from flask import Flask, request, jsonify
import logging
from unpack.unpack import get_value

'''
Flask app that takes in zipped 3d model file, JSON data, and Sketchfab API
token and publishes to Sketchfab.

Returns JSON object with two fields, if successful, indicating Sketchfab UID
and permalink to hosted model location.

JSON data can be arbitrary: needs at least a 'name' field for the title of the
published model. Everything else can get dumped into a 'description' field.

'''

app = Flask(__name__) 

# logging boilerplate
service_name = str(os.path.basename(__file__))
logfile = 'service.log'
logging.basicConfig(level=logging.DEBUG, filename=logfile)
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info(f'Starting {service_name}...')

@app.route('/log', methods=['GET'])
def log_handler():
    try:
        with open(logfile, 'r') as f:
            l = f.read()
            ll = l.split('\n')
        return jsonify({'log': ll})
    except Exception as err:
        logging.error(f'/log error: {str(err)}')
        return jsonify({'err': str(err)})


@app.route('/', methods=['POST', 'GET', 'DELETE'])
def models():
    # Posts the model to sketchfab.
    if request.method == 'POST':
        try:
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
            name = metadata.get('object_title')
            description = metadata.get('description')
            data = {
                'name': name,
                'description': description,
                'isInspectable': True,
                'license': 'by'
                }
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
                logging.debug(f'response: {response}')
                uid = response.get('uid')
                if os.path.exists('model.zip'):
                    os.remove('model.zip')
                return jsonify({"resource_id": uid, "location": f"https://sketchfab.com/models/{uid}/embed"})
        except requests.exceptions.RequestException as e:
            return jsonify({'requestException': e})

    # Deletes the model from sketchfab.
    if request.method == 'DELETE':
        try:
            uid = get_value(request, 'data', 'resource_id')
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
        except requests.exceptions.RequestException as e:                  
            return jsonify({'requestException': str(e)})

    # Returns the details of the model.
    # if request.method == 'GET':
    #     try:
    #         uid = get_value(request, 'data', 'uid')
    #         SKETCHFAB_DOMAIN = 'sketchfab.com'
    #         SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
    #         token = get_value(request, 'config', 'token')
    #         headers = {'Authorization': 'Token {}'.format(token)}
    #         model_endpoint = SKETCHFAB_API_URL + '/models/{}'.format(uid)
    #         r = requests.get(model_endpoint, headers=headers)
    #     except requests.exceptions.RequestException as e:
    #         return jsonify({'requestException': e})
    #     else:
    #         response = r.json()
    #         print(response)
    #         return jsonify(response)

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


@app.route('/me', methods=['GET'])
def me():
    # Get the user information
    if request.method == 'GET':
        try:
            SKETCHFAB_DOMAIN = 'sketchfab.com'
            SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
            MODEL_ENDPOINT1 = SKETCHFAB_API_URL + '/me'
            MODEL_ENDPOINT2 = SKETCHFAB_API_URL + '/me/followers'
            MODEL_ENDPOINT3 = SKETCHFAB_API_URL + '/me/collections'
            MODEL_ENDPOINT4 = SKETCHFAB_API_URL + '/me/backgrounds'
            MODEL_ENDPOINT5 = SKETCHFAB_API_URL + '/me/followings'
            MODEL_ENDPOINT6 = SKETCHFAB_API_URL + '/me/subscriptions'
            MODEL_ENDPOINT7 = SKETCHFAB_API_URL + '/me/models'
            MODEL_ENDPOINT8 = SKETCHFAB_API_URL + '/me/likes'
            MODEL_ENDPOINT9 = SKETCHFAB_API_URL + '/me/environments'
            ALL_ENDPOINT = [MODEL_ENDPOINT1, MODEL_ENDPOINT2, MODEL_ENDPOINT3, MODEL_ENDPOINT4, MODEL_ENDPOINT5, MODEL_ENDPOINT6, MODEL_ENDPOINT7, MODEL_ENDPOINT8, MODEL_ENDPOINT9]

            config = json.loads(request.form.get('config'))
            auth = config.get('auth')
            token = auth.get('token')
            headers = {'Authorization': 'Token {}'.format(token)}
            resp_obj = {}
        
            for x in ALL_ENDPOINT:
                try:
                    r = requests.get(x, headers=headers)
                    resp_obj.update({x: r.json()})
                except requests.exceptions.RequestException as e:
                    resp_obj.update({x: str(e)})
            return jsonify(resp_obj)
        except requests.exceptions.RequestException as e:
            return jsonify({'requestException': str(e)})
            

if __name__ == '__main__':
    app.run() 