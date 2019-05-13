import requests
from flask import flash
from threedeposit.database import db_session, Deposit, Config
from threedeposit.admin.utils import _get_request_payload

SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v3'.format(SKETCHFAB_DOMAIN)
DELETE_ENDPOINT = SKETCHFAB_API_URL + '/models/'


def delete_models(scope):
    token = Config.query.filter_by(key='token').value(Config.value)

    if scope:
        if scope == 'DELETE_ALL':
            uids = []
            models = Deposit.query.filter(Deposit.sketchfab_uid is not None).all()
            model_count = len(models)
            if model_count > 0:
                for m in models:
                    uid = str(m.sketchfab_uid)
                    uids.append(uid)
                    r = requests.delete(DELETE_ENDPOINT + uid, **_get_request_payload())
                    # TODO make data update function
                    m.sketchfab_uid = None
                    m.sketchfab_url = None
                    m.sketchfab_thumbnail = '/static/default-thumbnail.jpg'
                    db_session.commit()
                    flash('Deleted: ' + uid, 'danger')
        else:
            print(scope)
            m = Deposit.query.filter_by(sketchfab_uid=scope).first()
            r = requests.delete(DELETE_ENDPOINT + scope, **_get_request_payload())
            m.sketchfab_uid = None
            m.sketchfab_url = None
            m.sketchfab_thumbnail = None
            db_session.commit()
            flash('Deleted: ' + scope, 'danger')
