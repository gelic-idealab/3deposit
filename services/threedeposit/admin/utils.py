from flask import current_app, flash
from threedeposit.database import Config
import requests
import json

# db_config = Accounts.query.order_by(Accounts.id.desc()).first()
# if db_config:
#     token = db_config.sketchfab_api_token
# else:
#     token = ''

SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
MODELS_ENDPOINT = SKETCHFAB_API_URL + '/me/models'
username = 'uiuclibrary'

uids = []


def _get_request_payload(data={}, files={}, json_payload=False):
    TOKEN = Config.query.filter_by(key='token').value(Config.value)
    """Helper method that returns the authentication token and proper content
    type depending on whether or not we use JSON payload."""
    headers = {'Authorization': 'Token {}'.format(TOKEN)}
    if json_payload:
        headers.update({'Content-Type': 'application/json; charset=utf-8'})
        data = json.dumps(data)
    return {'data': data, 'files': files, 'headers': headers}


def list_my_models():
    try:
        r = requests.get(MODELS_ENDPOINT, **_get_request_payload())
    except requests.exceptions.RequestException as e:
        current_app.logger.info('An API error occurred: {}'.format(e))
        flash('An API error occurred: {}'.format(e), category='danger')
    else:
        print(r)
        data = r.json().get('results')
        return data


def get_model_details(uid):
    try:
        r = requests.get(SKETCHFAB_API_URL + '/models' + '/{}'.format(uid))
    except requests.exceptions.RequestException as e:
        current_app.logger.info('An API error occurred: {}'.format(e))
    else:
        data = r.json()
        return data


def get_collections():
    try:
        r = requests.get(SKETCHFAB_API_URL + '/collections?user={}'.format(username))
    except requests.exceptions.RequestException as e:
        current_app.logger.info('An API error occurred: {}'.format(e))
    else:
        data = r.json()['results']
        return data


def get_collection(uid):
    try:
        r = requests.get(SKETCHFAB_API_URL + '/collections?user={}&uids={}'.format(username, uid))
    except requests.exceptions.RequestException as e:
        current_app.logger.info('An API error occurred: {}'.format(e))
    else:
        try:
            data = r.json()['results'][0]
            return data
        except Exception as e:
            flash('No collection data to return: {}'.format(e), category='danger')
