import os
import json
import requests
import vimeo
from flask import Flask, request, jsonify
import unpack

'''
Flask app that takes in 360 video file, JSON data, and credentials 
and publishes to Vimeo. 

'''

app = Flask(__name__)

@app.route('/vimeo', methods=['POST', 'GET'])

def post_to_vimeo():
    if request.method == 'POST':
        try:
            access_token = get_value(request, 'config', 'access_token')
            client_id = get_value(request, 'config', 'client_id')
            client_secret = get_value(request, 'config', 'client_secret')
        except Exception as err:
            return jsonify({'err': str(err)})

        # construct request
        client = vimeo.VimeoClient(
            token=access_token,
            key=client_id,
            secret=client_secret
        )

        try:
            # unpack payload
            name = get_value(request, 'data', 'name')
            description = get_value(request, 'data', 'description')
            filename = get_value(request, 'data', 'filename')
            projection = get_value(request, 'data', 'projection')
            stereo_format = get_value(request, 'data', 'stereo_format')

            file = request.files.get('file')
            if file and filename:
                file.save(filename)

                uri = client.upload(filename, data={
                    'name': name,
                    'description': description,
                    'spatial.projection': projection,
                    'spatial.stereo_format': stereo_format
                })

                os.remove(filename)
                return jsonify({'uri': uri})
            else:
                return jsonify({'err': 'No file provided'})
        except Exception as err:
            return jsonify({'err': str(err)})

    if request.method == 'GET':
        try:
            access_token = get_value(request, 'config', 'access_token')
            client_id = get_value(request, 'config', 'client_id')
            client_secret = get_value(request, 'config', 'client_secret')
        except Exception as err:
            return jsonify({'err': str(err)})

        # construct request
        client = vimeo.VimeoClient(
            token=access_token,
            key=client_id,
            secret=client_secret
        )

        # try:

        #         return jsonify({'err': 'No data retrieved'})
        # except Exception as err:
        #     return jsonify({'err': str(err)})

if __name__ == '__main__':
    app.run(debug=True)
