import os
import sys
import json
from flask import Flask, request, jsonify
from boxsdk import Client, OAuth2


app = Flask(__name__)

@app.route('/box', methods=['POST'])
def box():
    if request.method == 'POST':
        response = {}
        post_data = json.loads(request.form.get('data'))
        metadata = post_data.get('metadata')
        file_path = metadata['deposit_id']
        file = request.files['file']
        file.save(file_path)

        folder_id = post_data.get('services').get('box').get('folder_id')

        # reads tokens
        def read_tokens():
            tokens = {}
            tokens['at'] = post_data.get('auth').get('at')
            tokens['rt'] = post_data.get('auth').get('rt')
            return tokens


        def store_tokens(at, rt):
            response['auth']['at'] = at
            response['auth']['rt'] = rt
            print(rt)

    
        CLIENT_ID = post_data.get('auth').get('client_id')
        CLIENT_SECRET = post_data.get('auth').get('client_secret')

        oauth = OAuth2(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                store_tokens=store_tokens
                )

        tokens = read_tokens()
        oauth._access_token = tokens['at']
        oauth._refresh_token = tokens['rt']

        client = Client(oauth)
        archive = client.folder(folder_id=folder_id)
        try:
            upload_file = archive.upload(file_path)
            try:
                file_url = upload_file.get_shared_link_download_url(access='open')
                response['file_url'] = file_url
            except Exception as e:
                response['link error'] = str(e)
        except Exception as e:
            response['upload error'] = str(e)

    os.remove(file_path)
    return jsonify(response)        


if __name__ == '__main__':
    app.run()