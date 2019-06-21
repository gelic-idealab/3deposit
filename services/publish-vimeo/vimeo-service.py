import os
import json
import requests
import vimeo
from flask import Flask, request, jsonify
from unpack import get_value

'''
Flask app that takes in 360 video file, JSON data, and credentials 
and publishes to Vimeo. 

'''

app = Flask(__name__)

@app.route('/vimeo', methods=['POST', 'GET'])

def post_to_vimeo():
    if request.method == 'POST':
        try:
            access_token = unpack.get_value(request, 'config', 'access_token')
            client_id = unpack.get_value(request, 'config', 'client_id')
            client_secret = unpack.get_value(request, 'config', 'client_secret')
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
            name = unpack.get_value(request, 'data', 'name')
            description = unpack.get_value(request, 'data', 'description')
            filename = unpack.get_value(request, 'data', 'filename')
            projection = unpack.get_value(request, 'data', 'projection')
            stereo_format = unpack.get_value(request, 'data', 'stereo_format')

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
                return jsonify({'res': {'uri': uri}})
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

        try:
            if:
                videos = client.get('https://api.vimeo.com/channels/{channel_id}/videos')
                followers = client.get('https://api.vimeo.com/channels/{channel_id}/users')
                comments = client.get('https://api.vimeo.com/videos/{video_id}/comments')
                return jsonify({'res': {
                                    'all_videos': videos,
                                    'all_followers': followers,
                                    'all_comments': comments
                        })
            else:
                return jsonify({'err': 'No data provided'})
        except Exception as err:
            return jsonify({'err': str(err)})

if __name__ == '__main__':
    app.run(debug=True)
