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
        try:
            # unpack payload
            post_data = request.form.get('data')

            if post_data:
                auth = post_data.get('auth')
                if auth:
                    access_token = auth.get('token')
                    client_id = auth.get('clientid')
                    client_secret = auth.get('clientsecret')
                else:
                    return jsonify({"err": "No auth provided"})
            
                metadata = post_data.get('metadata')
                if metadata:
                    name = metadata.get('name')
                    description = metadata.get('description')
                    filename = metadata.get('filename')
                    projection = metadata.get('projection')
                    stereo_format = metadata.get('stereo_format')
            else:
                return jsonify({"err": "No post data"})
            file = request.files.get('files')
            if file and filename:
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
            else:
                return jsonify({"err": "No file provided"})
        except Exception as err:
            return jsonify({"err": err})

if __name__ == '__main__':
    app.run(debug=True)