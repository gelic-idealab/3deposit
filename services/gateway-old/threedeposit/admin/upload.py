import requests
import urllib
import os
from flask import flash
from threedeposit.database import db_session, Deposit, Config
from threedeposit.admin.utils import _get_request_payload


SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
MODEL_ENDPOINT = SKETCHFAB_API_URL + '/models'


def upload_models():
    uploaded_models = []

    # get deposits that have not been uploaded
    deposits = Deposit.query.filter_by(sketchfab_uid=None)

    for deposit in deposits:
        # create payload from deposit data
        data = {
            'name': deposit.deposit_title,
            'description': deposit.deposit_description,
            'tags': deposit.deposit_tags,
            # 'categories': categories,
            # 'license': license,
            # 'private': private,
            # 'password': password,
            # 'isPublished': isPublished,
            # 'isInspectable': isInspectable
            # 'options':json.dumps({'orientation':{'axis':[1,1,1], 'angle':0}})
            }

        box_model_path = deposit.box_model_path
        deposit_file_name = deposit.deposit_url.split('/')[-1]
        if box_model_path:
            # Download the file and save it locally
            dirname = os.path.dirname(__file__)
            tmp_path = os.path.join(dirname, 'tmp', deposit_file_name)
            try:
                with urllib.request.urlopen(box_model_path) as response, open(tmp_path, 'wb') as tmp_file:
                    file_data = response.read()
                    tmp_file.write(file_data)
                    tmp_file.close()
                f = open(tmp_path, 'rb')
                b = os.path.getsize(tmp_path)
            except Exception as e:
                print('could not open Box file: {}'.format(e))
            else:
                file = {'modelFile': f}
                # upload to Sketchfab
                try:
                    r = requests.post(MODEL_ENDPOINT, **_get_request_payload(data=data, files=file))
                except requests.exceptions.RequestException as e:
                    flash('An error occurred: {}'.format(e), category='danger')
                finally:
                    f.close()

                if r.status_code != requests.codes.created:
                    flash('Upload failed with error: {}'.format(r.reason) +
                          ' ' + str(r.status_code), category='danger')
                    os.remove(tmp_path)
                else:
                    model_url = r.headers['Location']
                    model_uid = model_url.split('/')[-1]
                    # dt_format = '%m/%d/%y %I:%M:%S %p'

                    # add upload data to deposit row
                    deposit.sketchfab_uid = model_uid
                    deposit.sketchfab_url = model_url
                    # TODO add response code to deposit table
                    db_session.commit()
                    uploaded_models.append(model_uid)

                    # clean up tmp file
                    os.remove(tmp_path)
                    flash('{} successfully uploaded'.format(model_uid), category='success')            

    return uploaded_models
