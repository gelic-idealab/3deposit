from flask import flash, request
from threedeposit.database import db_session, Config


def post_configs():
    # folderid = request.form.get('folderid')
    # token = request.form.get('token')
    # collectionid = request.form.get('collectionid')
    # formid = request.form.get('formid')
    # key1 = request.form.get('key1')
    # key2 = request.form.get('key2')
    # key3 = request.form.get('key3')

    # db_config = Accounts(box_folder_id=folderid,
    #                      sketchfab_api_token=token,
    #                      sketchfab_collection_id=collectionid,
    #                      webtools_form_id=formid,
    #                      webtools_key_1=key1,
    #                      webtools_key_2=key2,
    #                      webtools_key_3=key3)

    f = request.form
    for key in f.keys():
        for value in f.getlist(key):
            exists = Config.query.filter_by(key=key).scalar()
            if exists:
                Config.query.filter_by(key=key).update(dict(value=value))
                db_session.commit()
                flash(f'Configuration for {key} updated', category='success')
            else:
                add_config = Config(key=key, value=value)
                db_session.add(add_config)
                db_session.commit()
                flash(f'Configuration for {key} added', category='success')

    # db_session.add(db_config)
    # db_session.commit()
    # flash('Account configuration updated', category='success')
    # return(folderid, token, collectionid, formid, key1, key2, key3)


# def get_configs():
    
#     # db_config = Accounts.query.order_by(Accounts.id.desc()).first()

#     # if db_config:
#     #     folderid = db_config.box_folder_id
#     #     token = db_config.sketchfab_api_token
#     #     collectionid = db_config.sketchfab_collection_id
#     #     formid = db_config.webtools_form_id
#     #     key1 = db_config.webtools_key_1
#     #     key2 = db_config.webtools_key_2
#     #     key3 = db_config.webtools_key_3

#     # else:
#     #     folderid = ''
#     #     token = ''
#     #     collectionid = ''
#     #     formid = ''
#     #     key1 = ''
#     #     key2 = ''
#     #     key3 = ''

#     folderid = Config.query.filter_by(key='folderid').value(Config.value)
#     token = Config.query.filter_by(key='token').value(Config.value)
#     collectionid = Config.query.filter_by(key='collectionid').value(Config.value)
#     formid = Config.query.filter_by(key='formid').value(Config.value)
#     key1 = Config.query.filter_by(key='key1').value(Config.value)
#     key2 = Config.query.filter_by(key='key2').value(Config.value)
#     key3 = Config.query.filter_by(key='key3').value(Config.value)

#     return(folderid, token, collectionid, formid, key1, key2, key3)
