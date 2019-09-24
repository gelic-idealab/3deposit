import os
import json
import requests
import vimeo
from flask import Flask, request, jsonify
import zipfile
import logging


'''
Flask app that takes in 360 video file, JSON data, and credentials 
and publishes to Vimeo. 
'''

app = Flask(__name__)

# logging boilerplate
service_name = str(os.path.basename(__file__))
logfile = 'service.log'
logging.basicConfig(level=logging.DEBUG, filename=logfile)
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info('Starting {}...'.format(service_name))

@app.route('/log', methods=['GET'])
def log_handler():
    try:
        with open(logfile, 'r') as f:
            l = f.read()
            ll = l.split('\n')
        return jsonify({'log': ll})
    except Exception as err:
        logging.error('/log error: {}'.format(str(err)))
        return jsonify({'err': str(err)})


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
            did = data.get('deposit_id')
            metadata = data.get('metadata')

            logging.info('POST request for deposit_id: {}; metadata: {}'.format(did, str(metadata)))

            title = str(metadata.get('object_title'))
            description = str(metadata.get('description'))
            projection = str(metadata.get('projection'))
            stereo_format = str(metadata.get('stereo_format'))

            file = request.files.get('file')
            if file and did:
                fzip = did
                file.save(fzip)

                with zipfile.ZipFile(fzip, 'r') as zip_ref:
                    filename = zip_ref.namelist()[0]
                    zip_ref.extract(filename)
                try:
                    uri = client.upload(filename, data={
                        'name': title,
                        'description': description,
                          'spatial': {
                              'projection': projection,
                              'stereo_format': stereo_format
                          }
                    })
                except Exception as err:
                    logging.error(str(err))
                    return jsonify({'resource_id': 'Error uploading: ' + str(err), 'location': 'None'})

                try:
                    resource_id = uri.split('/')[-1]
                    return jsonify({'resource_id': resource_id, 'location': 'https://player.vimeo.com/video/{}'.format(resource_id)})
                except Exception as err:
                    logging.error(str(err))
                    return jsonify({'resource_id': 'Error reading upload response: ' + str(err), 'location': 'None'})
            else:
                return jsonify({'err': 'No file provided'})
        except Exception as err:
            logging.error(str(err))
            return jsonify({'resource_id': 'Error reading request data: ' + str(err), 'location': 'None'})
            
        finally:
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(fzip):
                os.remove(fzip)

    elif request.method == 'GET':
        try:
            data = json.loads(request.form.get('data'))
            video_id = data.get('resource_id')
            url = 'https://api.vimeo.com/videos/{}'.format(video_id)
            r = client.get(url)
            return jsonify(r.json())
        except Exception as err:
            logging.error(str(err))
            return jsonify({'err': str(err)})

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.form.get('data'))
            video_id = data.get('resource_id')
            url = '/videos/{}'.format(video_id)
            r = client.delete(url)
            return jsonify(r.json())
        except Exception as err:
            logging.error(str(err))
            return jsonify({'err': str(err)})


if __name__ == '__main__':
    app.run()
