import os
import json
import requests
import vimeo
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/vimeo', methods=['POST', 'GET', 'DELETE'])
def vimeo_service():
    config = json.loads(request.form.get('config'))
    auth = config.get('auth')
    access_token = auth.get('access_token')
    client_id = auth.get('client_id')          
    client_secret = auth.get('client_secret')
    client = vimeo.VimeoClient(
        token=access_token,
        key=client_id,
        secret=client_secret
    )

    if request.method == 'POST':
        try:
            data = json.loads(request.form.get('data'))
            name = data.get('name')
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
                    'projection': projection,
                    'stereo_format': stereo_format
                })
                os.remove(filename)
                return jsonify({'res': {'uri': uri}})
            else:
                return jsonify({'err': 'No file provided'})
        except Exception as err:
            return jsonify({'err': str(err)})

    elif request.method == 'GET':
        try:
            api = 'https://api.vimeo.com/'
            data = json.loads(request.form.get('data'))
            video_id = data.get('video_id')
            get_video = client.get('{}videos/{}'.format(api, video_id))
            get_comments = client.get('{}videos/{}/comments'.format(api, video_id))
            if get_video and get_comments:
                return jsonify({'res': {'video': get_video,
                                        'comments': get_comments
                        }})
            else:
                return jsonify({'err': 'No data provided'})
        except Exception as err:
            return jsonify({'err': str(err)})

    elif request.method == 'DELETE':
        try:
            api = 'https://api.vimeo.com/'
            data = json.loads(request.form.get('data'))
            video_id = data.get('video_id')
            del_video = client.delete('{}videos/{}'.format(api, video_id))
            if del_video:
                return jsonify({'res': 'Video deleted successfully'})
            else:
                return jsonify({'err': 'No video deleted'})
        except Exception as err:
            return jsonify({'err': str(err)})

if __name__ == '__main__':
    app.run(debug=True)
