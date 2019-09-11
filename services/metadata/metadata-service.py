import os
import json
import requests
from flask import Flask, request, jsonify
import logging

import pymediainfo
# https://pymediainfo.readthedocs.io/en/stable/


'''
Flask app that generates & harvests metadata from 3d media, 
handles POST requests with media payload, responds with metadata. 
'''

app = Flask(__name__)

# logging
logging.basicConfig(level=logging.DEBUG)
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.route('/', methods=['POST', 'GET', 'DELETE'])
def handler():

    # get auth values from request object
    config = json.loads(request.form.get('config'))
    auth = config.get('auth')


if __name__ == '__main__':
    app.run()