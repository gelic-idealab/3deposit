import os
import db
import logging
import json

import db
from aiopg.sa import create_engine
from aiohttp import web, FormData, ClientSession
from aiohttp import request as new_request
from settings import get_config


TMP_FILE_LOCATION = './data/{}'

async def get_service_engine():
    conf = get_config()['postgres']
    engine = await create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    return engine


"""
Trigger function to begin storage operation with buffered deposit file
"""


async def start_deposit_processing_task(data):
    try:
        engine = await get_service_engine()

        deposit_id = data.get('id')
        media_type = data.get('media_type')
        if deposit_id:
            logging.debug(msg=f'start_deposit_processing_task id: {str(deposit_id)}')
            async with engine.acquire() as conn:
                await db.add_deposit_by_id(conn, deposit_id)
                etag = await trigger_store(conn, deposit_id)
                mongo_id = await trigger_metadata(data)
                publish_resp = await trigger_publish(conn, data)
                await db.update_deposit_by_id(
                    conn,
                    deposit_id=deposit_id,
                    etag=etag,
                    mongo_id=mongo_id,
                    resource_id=publish_resp.get('resource_id'),
                    media_type=media_type
                )

                data = {
                    'location': publish_resp.get('location'),
                    'resource_id': publish_resp.get('resource_id')
                }

                config = {
                    'deposit_id': deposit_id
                }

                fd = FormData()
                fd.add_field('data', json.dumps(data), content_type='application/json')
                fd.add_field('config', json.dumps(config), content_type='application/json')

                async with new_request(method='PATCH', url='http://mongo-service:5000/objects', data=fd) as resp:
                    resp_json = await resp.json()
                    if resp_json.err:
                        logging.error(resp_json.err)
                    else:
                        logging.info(resp_json.log)

            if os.path.exists(TMP_FILE_LOCATION.format(deposit_id)):
                os.remove(TMP_FILE_LOCATION.format(deposit_id))
            return True
        else:
            return False
    except Exception as err:
        logging.debug(msg=str(err))
        return False


async def trigger_store(conn, did):
        # async with ClientSession() as sess:
        #     async with sess.request(url='/store/objects', method='POST', data=fd, params=deposit_id) as resp:
        #         resp_json = await resp.json()
        #         etag = resp_json.get('etag')
        #         logging.debug(msg=f'trigger_store resp: {str(resp_json)}, {etag}')
        #         return etag

    PATH = '/object'
    service_config = await get_service_config_by_action(conn=conn, action='store', media_type='default')
    logging.debug(msg='trigger_store service_config: {}'.format(str(service_config)))
    config = dict(service_config.get('config'))
    endpoint = service_config.get('endpoint')
    bucket_name = dict({'bucket_name': '3deposit'})
    config.update(bucket_name)

    with open(TMP_FILE_LOCATION.format(did), 'rb') as f:
        try:
            deposit_id = dict({'deposit_id': did})
            fd = FormData()
            fd.add_field('file', f, filename=did, content_type='application/octet-stream')
            fd.add_field('config', json.dumps(config), content_type='application/json')
            fd.add_field('data', json.dumps(deposit_id), content_type='application/json')
            async with new_request(method='POST', url=endpoint+PATH, data=fd) as resp:
                resp_json = await resp.json()
                etag = resp_json.get('etag')
                logging.debug(msg=f'trigger_store resp: {str(resp_json)}, {etag}')
                return etag

        except Exception as err:
            return web.json_response({'origin': 'gateway', 'err': str(err)})


def extract_data_from_form(form):
    form_data = {}
    for field in form:
        form_data.update({field.get('id'): field.get('value')})
    return form_data


async def trigger_publish(conn, data):
    media_type = data.get('media_type')
    service_config = await get_service_config_by_action(conn=conn, action='publish', media_type=media_type)
    logging.debug(msg='service_config: {}'.format(str(service_config)))
    service_name = service_config.get('name')
    did = data.get('id')
    form = data.get('form')
    metadata = extract_data_from_form(form)
    logging.debug(msg="PUBLISH METADATA "+str(metadata))
    data = {}
    data.update({'metadata': metadata})
    data.update({'deposit_id': did})
    fd = FormData()
    fd.add_field('data', json.dumps(data), content_type='application/json')
    service_config = await db.get_service_config(conn=conn, name=service_name)
    if service_config:
        endpoint = service_config.get('endpoint')
        config = service_config.get('config')
        fd.add_field('config', json.dumps(config), content_type='application/json')
        with open(TMP_FILE_LOCATION.format(did), 'rb') as f:
            fd.add_field('file', f, filename=did, content_type='application/octet-stream')
            logging.debug(msg="ENDPOINT: "+endpoint+"FORM DATA: "+str(data))
            async with new_request(method='POST', url=endpoint, data=fd) as resp:
                logging.debug(msg="PUBLISH RESPONSE: "+str(await resp.text()))
                resp_json = await resp.json()
                return resp_json


async def trigger_metadata(data):
    did = data.get('id')
    form = data.get('form')
    form_data = extract_data_from_form(form)
    deposit_metadata = dict({'deposit_metadata': form_data})
    deposit_id = dict({'deposit_id': did})
    data = {}
    data.update(deposit_id)
    data.update(deposit_metadata)
    fd = FormData()
    fd.add_field('data', json.dumps(data), content_type='application/json')
    async with new_request(method='POST', url='http://mongo-service:5000/objects', data=fd) as resp:
        resp_json = await resp.json()
        mongo_id = resp_json.get('mongo_id')
        return mongo_id


"""
Helper function to return service configs for a given action and media_type
"""


async def get_service_config_by_action(conn, action, media_type):
    try:
        logging.debug(msg='get_service_config_by_action called with: {}, {}'.format(action, media_type))
        action_service_name = await db.get_action_service_name(conn=conn, action=action, media_type=media_type)
        logging.debug(msg='action_service_name: {}'.format(action_service_name))
        service_config = await db.get_service_config(conn=conn, name=action_service_name)
        if service_config:
            return service_config
        else:
            return None
    except Exception as err:
        logging.debug(msg='get_service_config_by_action err: {}'.format(str(err)))
