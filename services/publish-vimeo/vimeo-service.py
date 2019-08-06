import os
import json
import requests
import vimeo
from flask import Flask, request, jsonify

'''
Flask app that takes in 360 video file, JSON data, and credentials 
and publishes to Vimeo. 
'''

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET', 'DELETE'])
def handler():

    # get auth values from request object
    config = json.loads(request.form.get('config'))
    auth = config.get('auth')
    access_token = auth.get('access_token')
    client_id = auth.get('client_id')          
    client_secret = auth.get('client_secret')

    # construct client
    client = vimeo.VimeoClient(
        token=access_token,
        key=client_id,
        secret=client_secret
    )

    if request.method == 'POST':
        try:
            # unpack payload
            data = json.loads(request.form.get('data'))
            data = data.get('metadata')
            name = data.get('object_title')
            description = data.get('description')
            filename = data.get('filename')
            projection = data.get('projection')
            stereo_format = data.get('stereo_format')

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
                resource_id = uri.split('/')[-1]
                return jsonify({"resource_id": resource_id, "location": "https://player.vimeo.com/video/{}".format(resource_id)})
            else:
                return jsonify({'err': 'No file provided'})
        except Exception as err:
            return jsonify({'err': str(err)})

    else:
        try:
            data = json.loads(request.form.get('data'))
            video_id = data.get('resource_id')
            url = '/videos/{}/pictures'.format(video_id)
            if request.method == 'GET':
                r = client.get(url)
            elif request.method == 'DELETE':
                r = client.delete(url)
            return jsonify(r.json())
        except Exception as err:
            return jsonify({'err': str(err)})


if __name__ == '__main__':
    app.run()
