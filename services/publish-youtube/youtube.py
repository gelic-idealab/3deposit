import os
import json
import requests
# import google-api-python-client
# see imports from sample below
from flask import Flask, request, jsonify

'''
Flask app that takes in zipped 360 video file, JSON data, and credentials 
and publishes to YouTube360. 

'''

app = Flask(__name__)

@app.route('/youtube', methods=['POST'])
def youtube():
    if request.method == 'POST':
        # build post request to YouTube
        # see https://github.com/youtube/api-samples/blob/master/python/upload_video.py
        # pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 
        
        post_data = json.loads(request.form.get('data'))
        token = post_data.get('token')
        headers = {'Authorization': 'Token {}'.format(token)}
        
        filename = post_data.get('metadata').get('filename')

        file = request.files['file']
        file.save(filename)
        

        return jsonify({'message': 'post received'})


if __name__ == '__main__':
    app.run()