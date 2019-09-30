import os
import db
import logging
import json
from asyncio import create_task
import shutil

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

async def start_reassembling_chunks(did):
    try:
        tmp_deposit_dir = f'./data/{did}_chunks/'
        with open(f'./data/{did}', 'wb') as f:
            chunk_to_write = 1
            num_chunks = len(os.listdir(tmp_deposit_dir))
            while chunk_to_write <= int(num_chunks):
                current_chunk = tmp_deposit_dir+str(chunk_to_write)
                with open(current_chunk, 'rb') as c:
                    f.write(c.read())
                    os.remove(current_chunk)
                    chunk_to_write += 1
            return True
    except Exception as err:
        logging.error(msg=f'start_reassembling_chunks err: {str(err)}')
        return False
    finally:
        shutil.rmtree(tmp_deposit_dir)
        

async def start_deposit_processing_task(data):
    try:
        deposit_id = data.get('id')

        logging.info(msg='start_deposit_processing_task'+str(data))
        assemble_chunks = create_task(start_reassembling_chunks(deposit_id))
        chunks_assembled = await assemble_chunks
        if chunks_assembled:
            engine = await get_service_engine()
            media_type = data.get('media_type')
            if deposit_id:
                async with engine.acquire() as conn:
                    # insert deposit_id
                    await db.add_deposit_by_id(conn, deposit_id)
                    await db.update_deposit_by_id(
                        conn,
                        deposit_id=deposit_id,
                        media_type=media_type,
                        deposit_date=data.get('deposit_date')
                    )

                    # update with etag
                    etag = await trigger_store(conn, deposit_id)
                    await db.update_deposit_by_id(
                        conn,
                        deposit_id=deposit_id,
                        etag=etag
                    )

                    # update with mongo_id
                    mongo_id = await trigger_metadata(data)
                    await db.update_deposit_by_id(
                        conn,
                        deposit_id=deposit_id,
                        mongo_id=mongo_id
                    )

                    # update with resource_id and location
                    publish_resp = await trigger_publish(conn, data)
                    await db.update_deposit_by_id(
                        conn,
                        deposit_id=deposit_id,
                        resource_id=publish_resp.get('resource_id')                        
                    )

                    # add new fields to mongo doc
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
                        if resp_json.get('err'):
                            logging.error(resp_json.get('err'))
                        else:
                            logging.info(resp_json.get('log'))

                if os.path.exists(TMP_FILE_LOCATION.format(deposit_id)):
                    os.remove(TMP_FILE_LOCATION.format(deposit_id))

                return True

            else:
                return False
        else:
            logging.error(msg=f'error assembling chunks')
            return False

    except Exception as err:
        logging.error(msg=f'start_deposit_processing_task err: {str(err)}')
        return False


async def trigger_store(conn, did):

    PATH = '/object'
    service_config = await get_service_config_by_action(conn=conn, action='store', media_type='default')
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
    service_name = service_config.get('name')
    did = data.get('id')
    form = data.get('form')
    metadata = extract_data_from_form(form)
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
            async with new_request(method='POST', url=endpoint, data=fd) as resp:
                resp_json = await resp.json()
                return resp_json


async def trigger_metadata(data):
    did = data.get('id')
    form = data.get('form')
    media_type = data.get('media_type')
    form_data = extract_data_from_form(form)
    deposit_date = data.get('deposit_date')
    form_data.update({'deposit_date': deposit_date})
    deposit_metadata = dict({'deposit_metadata': form_data})
    deposit_id = dict({'deposit_id': did})
    data = {}
    data.update({'deposit_date': deposit_date})
    data.update(deposit_id)
    data.update(deposit_metadata)

    fd = FormData()
    fd.add_field('data', json.dumps(data), content_type='application/json')

    with open(TMP_FILE_LOCATION.format(did), 'rb') as f:
        fd.add_field('file', f, filename=did, content_type='application/octet-stream')
        if media_type == 'video':
            async with new_request(method='POST', url='http://metadata-service:5000/', data=fd) as resp:
                resp_json = await resp.json()
                technical_metadata = resp_json.get('video_metadata')

    if technical_metadata:
        data.update({'technical_metadata': technical_metadata})

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
        action_service_name = await db.get_action_service_name(conn=conn, action=action, media_type=media_type)
        service_config = await db.get_service_config(conn=conn, name=action_service_name)
        if service_config:
            return service_config
        else:
            return None
    except Exception as err:
        logging.error(msg=f'get_service_config_by_action err: {str(err)}')
