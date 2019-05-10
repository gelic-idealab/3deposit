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

@app.route('/vimeo', methods=['POST'])
def post_to_vimeo():
    if request.method == 'POST':
        # unpack payload
        post_data = json.loads(request.form.get('data'))

        auth = post_data.get('auth')
        access_token = auth.get('token')
        client_id = auth.get('clientid')
        client_secret = auth.get('clientsecret')
        
        metadata = post_data.get('metadata')
        name = metadata.get('name')
        description = metadata.get('description')
        filename = metadata.get('filename')
        projection = metadata.get('projection')
        stereo_format = metadata.get('stereo_format')

        file = request.files['file']
        file.save(filename)

        # construct request
        client = vimeo.VimeoClient(
        token=access_token,
        key=client_id,
        secret=client_secret
        )

        file_name = filename
        uri = client.upload(file_name, data={
        'name': name,
        'description': description,
        'spatial':  {
                "stereo_format": stereo_format,
                "projection": projection
        }
        })

        os.remove(filename)

        return jsonify({'uri': uri})

if __name__ == '__main__':
    app.run()