import os
import json
import requests
import logging
import zipfile

from flask import Flask, request, jsonify
import pymediainfo
# https://pymediainfo.readthedocs.io/en/stable/


'''
Flask app that generates & harvests metadata from 3d media, 
handles POST requests with media payload, responds with metadata. 
'''

app = Flask(__name__)

# logging
logging.basicConfig(level=logging.DEBUG, filename='service.log')
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.route('/', methods=['POST', 'GET'])
def handler():

    try:
        # unpack request data
        data = json.loads(request.form.get('data'))
        did = data.get('deposit_id')
        deposit_form_metadata = data.get('metadata')

        logging.info(f"POST request for deposit_id: {did}, data: {deposit_form_metadata}")

        # unzip file payload
        file = request.files.get('file')
        if file and did:
            fzip = did
            file.save(fzip)

            with zipfile.ZipFile(fzip, 'r') as zip_ref:
                filename = zip_ref.namelist()[0]
                zip_ref.extract(filename)


            # extract metadata and return
    
    except Exception as err:
        logging.error(str(err))
        return jsonify({'err': str(err)})
    
    finally:
        if os.path.exists(did):
            os.remove(did)
        if os.path.exists(filename):
            os.remove(filename)


if __name__ == '__main__':
    app.run()