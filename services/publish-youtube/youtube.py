import os
import json
import requests
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
        
        post_data = json.loads(request.form.get('data'))
        token = post_data.get('token')
        headers = {'Authorization': 'Token {}'.format(token)}
        
        filename = post_data.get('metadata').get('filename')

        file = request.files['file']
        file.save(filename)
        

        return jsonify({'message': 'post received'})


if __name__ == '__main__':
    app.run()