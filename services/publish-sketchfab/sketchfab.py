import requests
import urllib
import os
import json
from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/publish', methods=['POST'])
def publish():
    
    # SKETCHFAB_DOMAIN = 'sketchfab.com'
    # SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
    # MODEL_ENDPOINT = SKETCHFAB_API_URL + '/models'
    # TOKEN = request.data.get('token')

    # headers = {'Authorization': 'Token {}'.format(TOKEN)}
    # post_data = request.data
    # deposit_data = post_data.get('deposit')
    # data = deposit_data.get('title')
    # files = {'modelFile': request.files}

    # # upload to Sketchfab
    # try:
    #     r = requests.post(MODEL_ENDPOINT, data=data, files=files, headers=headers)
    # except requests.exceptions.RequestException as e:
    #     return jsonify('An error occurred: {}'.format(e))
    # else:
    #     data = {}
    #     data['location'] = r.headers['Location']
    #     data['id'] = data['location'].split('/')[-1]

    #     return jsonify(data)

    data = request.form.get('data')
    token = request.form.get('token')
    file = request.files

    return jsonify(data=data, token=token, file=str(file.items))


if __name__ == '__main__':
    app.debug == True
    app.run()