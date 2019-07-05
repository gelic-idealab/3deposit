import json
import logging
import os
from asyncio import create_task

import db
import aiohttp_jinja2
from aiohttp import web, FormData, ClientSession
from aiohttp import request as new_request
from aiohttp_security import remember, forget, authorized_userid

import db
from forms import validate_login_form
from process import get_service_config_by_action, start_deposit_processing_task
import logging



def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)

"""
View endpoints for authorizing user

'index', 'login', and 'logout' validate user, store secure cookie
"""

@aiohttp_jinja2.template('index.html')
async def index(request):
    username = await authorized_userid(request)
    if not username:
        raise redirect(request.app.router, 'login')

    async with request.app['db'].acquire() as conn:
        current_user = await db.get_user_by_name(conn, username)

    return {'current_user': current_user}


@aiohttp_jinja2.template('login.html')
async def login(request):
    username = await authorized_userid(request)
    if username:
        raise redirect(request.app.router, 'index')

    if request.method == 'POST':
        form = await request.post()

        async with request.app['db'].acquire() as conn:
            error = await validate_login_form(conn, form)

            if error:
                return {'error': error}
            else:
                response = redirect(request.app.router, 'index')

                user = await db.get_user_by_name(conn, form['username'])
                await remember(request, response, user['username'])

                raise response

    return {}


async def logout(request):
    response = redirect(request.app.router, 'login')
    await forget(request, response)
    return response



"""
Helper function to relay form data with files
"""
# async def form_data_from_request(request):
#     fd = FormData()
#     auth = json.dumps({'auth': {'auth_key': 'auth_value'}})
#     data = json.dumps({'deposit_id': '12345'})
#     fd.add_field('config', auth, content_type='application/json')
#     fd.add_field('data', data, content_type='application/json')
#     fd.add_field('files', open('test.txt', 'rb'), filename='test.txt')
#     async with new_request.post(SERVICE_ENDPOINT, data=fd) as resp:
#         return web.json_response({"res": await resp.json() })


"""
Handlers for getting and setting services & service configs
"""

async def services(request):
    if request.method == 'GET':
        try:
            async with request.app['db'].acquire() as conn:
                services = await db.get_services(conn)
                if services:
                    return web.json_response({ 'services': services }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
                else:
                    return web.json_response({ 'res': 'no services'}, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
    else:
        return web.Response(headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

async def services_configs(request):

    headers = {
        'ACCESS-CONTROL-ALLOW-ORIGIN': '*',
        'Access-Control-Allow-Headers': 'content-type'
    }
    if request.method == 'GET':
        try:
            req = request.query
            async with request.app['db'].acquire() as conn:
                service_config = await db.get_service_config(conn=conn, name=req.get('name'))
                if service_config:
                    return web.json_response({ 'service_config': service_config }, headers=headers)
                else:
                    return web.json_response({ 'err': 'No matching service', 'req': req }, headers=headers)
        except Exception as err:
            return web.json_response({ 'err': str(err), 'req': req }, headers=headers)
    elif request.method == 'POST':
        """
        request.json():
        {
            "name": "minio",
            "endpoint": "http://minio-service:5000/bucket",
            "config": {
                "auth": {
                    "access_key": "AKIAIOSFODNN7GRAINGER",
                    "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY"
                }
            }
        }
        """
        try:
            req = await request.json()
            async with request.app['db'].acquire() as conn:
                service = await db.set_service_config(conn=conn, name=req.get('name'), endpoint=req.get('endpoint'), config=req.get('config'))
                if service:
                    return web.json_response({ 'res': service }, headers=headers)
                else:
                    return web.json_response({'req':str(req),'err':'Could not create service.'}, headers=headers)
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=headers)
    
    else:
        return web.Response(headers=headers)        

# async def services_actions(request):
#     if request.method == 'GET':
#         try:
#             q = request.query
#             action = q.get('action')
#             media_type = q.get('media_type')
#             if q:
#                 async with request.app['db'].acquire() as conn:
#                     service_name = await db.get_action_service_name(conn, action=action, media_type=media_type)
#                     if service_name:
#                         return web.json_response({ 'service_name': service_name }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
#                     else:
#                         return web.json_response({ 'res': 'no service configured for {}, {}'.format(action, media_type)}, 
#                         headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

#             async with request.app['db'].acquire() as conn:
#                 services = await db.get_action_services(conn)
#                 if services:
#                     return web.json_response({ 'services': services }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
#                 else:
#                     return web.json_response({ 'res': 'no action services'}, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
#         except Exception as err:
#             return web.json_response({ 'err': str(err) }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

          
async def services_actions(request):
    if request.method == 'GET':
        try:
            q = request.query
            action = q.get('action')
            media_type = q.get('media_type')
            if q:
                async with request.app['db'].acquire() as conn:
                    service_name = await db.get_action_service_name(conn, action=action, media_type=media_type)
                    if service_name:
                        return web.json_response({ 'service_name': service_name }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
                    else:
                        return web.json_response({ 'res': 'no service configured for {}, {}'.format(action, media_type)}, 
                        headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

            async with request.app['db'].acquire() as conn:
                services = await db.get_action_services(conn)
                if services:
                    return web.json_response({ 'services': services }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
                else:
                    return web.json_response({ 'res': 'no action services'}, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

    if request.method == 'POST':
        try:
            req = await request.json()
            async with request.app['db'].acquire() as conn:
                service = await db.set_action_service_name(conn=conn, action=req.get('action'), media_type=req.get('media_type'), service_name=req.get('service_name'))
                if service:
                    return web.json_response({ 'res': service }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

    else:
        return web.Response(headers={
        'ACCESS-CONTROL-ALLOW-ORIGIN': '*',
        'Access-Control-Allow-Headers': 'content-type'
    })

"""
Handlers for deposit form frontend
"""

async def deposit_form(request):
    if request.method == 'GET':
        form_id = request.query.get('id')
        if form_id is None:
            form_id = 1
        async with request.app['db'].acquire() as conn:
            form = await db.get_form_by_id(conn, id=form_id)
        if form:
            return web.json_response({ 'form': form }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
        else:
            return web.json_response({ 'err': f'No form with id {form_id}' }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

    if request.method == 'POST':
        try:
            req = await request.json()
            content = req.get('content')
            id = req.get('id')
            if content:
                try:
                    async with request.app['db'].acquire() as conn:
                        if id:
                            try:
                                await db.update_form_by_id(conn, req.get('id'), req.get('content'))
                                return web.json_response({ 'msg': f'Updated content for form {form_id}'})
                            except Exception as e:
                                return web.json_response({ 'err': f'Error updating form id {id}: ' + str(e) })
                        try:
                            created = await db.create_form(conn, content)
                            return web.json_response({ 'msg': str(created) })
                        except Exception as e:
                            return web.json_response({ 'err': 'Error creating form: ' + str(e) })
                except Exception as e:
                    return web.json_response({ 'err': str(e) })
        except Exception as e:
            return web.json_response({'err': 'Error handling request: ' + str(e) })


async def deposit_upload(request):
    headers = dict({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'})
    if request.method == 'POST':
        try:
            logging.debug(msg='query: {}'.format(request.query))
            reader = await request.multipart()
            did = request.query['deposit_id']
            logging.debug('uploading {}'.format(str(did)))
            rcn = int(request.query['resumableChunkNumber'])
            rtc = int(request.query['resumableTotalChunks'])
            while True:
                part = await reader.next()
                if part is None:
                    break
                if part.name == 'file':
                    if rcn == 1:
                        with open('./data/{}'.format(did+'_partial'), 'wb') as f:
                            b = await part.read()
                            f.write(b)
                    elif rcn > 1:
                        with open('./data/{}'.format(did+'_partial'), 'ab') as f:
                            b = await part.read()
                            f.write(b)
                    if rcn == rtc:
                        os.rename('./data/{}'.format(did+'_partial'), './data/{}'.format(did))
            return web.Response(status=200, headers=headers)       
        except Exception as err:
            logging.debug(msg='err: {}'.format(str(err)))
            return web.json_response({ 'err': str(err) }, headers=headers)
    else:
        return web.Response(status=200, headers=headers)


async def deposit_submit(request):
    headers = {
    'ACCESS-CONTROL-ALLOW-ORIGIN': '*',
    'Access-Control-Allow-Headers': 'content-type'
    }   
    if request.method == 'POST':
        try:
            data = await request.json()
            # logging.debug(msg=f'deposit_submit data: {data}')
            deposit_processed = create_task(start_deposit_processing_task(data))
            if deposit_processed:
                return web.Response(status=200, headers=headers)
            else:
                return web.Response(status=418, headers=headers)
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=headers)
    else:
        return web.Response(status=200, headers=headers)


"""
Relay endpoint to make object storage calls
Endpoints are scoped for objects and buckets
"""

async def store_buckets(request):
    PATH = '/bucket'
    async with request.app['db'].acquire() as conn:
        service_config = await get_service_config_by_action(conn=conn, action='store', media_type='default')
    config = service_config.get('config')
    endpoint = service_config.get('endpoint')
    if request.method == 'GET':
        try:
            data = request.query
            config.update({'bucket_name': data.get('bucket_name')})
            fd = FormData()
            fd.add_field('config', json.dumps(config), content_type='application/json')
            async with new_request(method='GET', url=endpoint+PATH, data=fd) as resp:
                try:
                    resp_json = await resp.json()
                except Exception as err:
                    return web.json_response({'err': str(err), 'resp': await resp.text()})
                return web.json_response({ 'resp': resp_json })
        except Exception as err:
            return web.json_response({ 'origin': 'gateway', 'err': str(err) })

    if request.method == 'POST':
        try:
            data = await request.json()
            fd = FormData()
            fd.add_field('config', json.dumps(config), content_type='application/json')
            fd.add_field('data', json.dumps(data), content_type='application/json')
            # payload = dict({'config': config, 'data': data})
            async with new_request(method='POST', url=endpoint+PATH, data=fd) as resp:
                resp_json = await resp.json()
                return web.json_response({ 'resp': resp_json })
        except Exception as err:
            return web.json_response({ 'origin': 'gateway', 'err': str(err) })


async def store_objects(request):
    PATH = '/object'
    async with request.app['db'].acquire() as conn:
        service_config = await get_service_config_by_action(conn=conn, action='store', media_type='default')
    logging.debug(msg='store_objects service_config: {}'.format(str(service_config)))
    config = dict(service_config.get('config'))
    endpoint = service_config.get('endpoint')
    bucket_name = dict({'bucket_name': '3deposit'})
    config.update(bucket_name)

    if request.method == 'GET':
        try:
            data = request.query
            config.update({'bucket_name': data.get('bucket_name')})
            payload = dict({'config': config})
            async with new_request(method='GET', url=endpoint+PATH, json=payload) as resp:
                try:
                    resp_json = await resp.json()
                except Exception as err:
                    return web.json_response({'err': str(err), 'resp': await resp.text()})
                return web.json_response({ 'resp': resp_json, 'payload': payload })
        except Exception as err:
            return web.json_response({ 'origin': 'gateway', 'err': str(err) })

    if request.method == 'POST':
        try:
            q = dict(request.query)
            fd = FormData()
            reader = await request.multipart()
            while True:
                part = await reader.next()
                if part is None:
                    break
                if part.name == 'file':
                    fd.add_field(name='file', value=await part.read(), filename=q.get('deposit_id'), content_type='application/octet-stream')
                else:
                    continue
            fd.add_field('config', json.dumps(config), content_type='application/json')
            fd.add_field('data', json.dumps(q), content_type='application/json')
            async with new_request(method='POST', url=endpoint+PATH, data=fd) as resp:
                resp_json = await resp.json()
                return web.json_response(resp_json)
        except Exception as err:
            return web.json_response({ 'origin': 'gateway', 'err': str(err) })


"""
Relay endpoint to get/post to Model publication service
"""
async def publish_models(request):
    PATH = '/models'
    async with request.app['db'].acquire() as conn:
        service_config = await get_service_config_by_action(conn=conn, action='publish', media_type='model')
    logging.debug(msg='service_config: {}'.format(str(service_config)))
    service_name = service_config.get('name')

    if request.method == 'GET':
        q = request.query
        data = {
            "uid": q.get('resource_id')
        }
        async with new_request(method='GET', url=endpoint+PATH, data=data) as resp:
            return web.json_response(await resp.json())
    
    # if request.method == 'POST':
    #     try:
    #         q = request.query
    #         did = q.get('deposit_id')
    #         metadata = await request.json()
    #         data = {}
    #         data.update({'metadata': metadata})
    #         fd = FormData()
    #         fd.add_field('data', json.dumps(data), content_type='application/json')
    #         async with request.app['db'].acquire() as conn:
    #             service_config = await db.get_service_config(conn=conn, name=service_name)
    #             if service_config:
    #                 endpoint = service_config.get('endpoint')
    #                 config = service_config.get('config')
    #                 fd.add_field('config', json.dumps(config), content_type='application/json')
    #                 with open('./data/{}'.format(did), 'rb') as f:
    #                     fd.add_field('file', f, filename=did, content_type='application/octet-stream')
    #                     async with new_request(method='POST', url=endpoint+PATH, data=fd) as resp:
    #                         resp_json = await resp.json()
    #                         uri = resp_json.get('uri')
    #                         return web.json_response(uri)
    #             else:
    #                 return web.json_response({ 'err': 'could not retrieve config for service: {}'.format(service_name)})
    #     except Exception as err:
    #         return web.json_response({ 'err': str(err) })


async def deposits(request):
    headers = {
    'ACCESS-CONTROL-ALLOW-ORIGIN': '*',
    'Access-Control-Allow-Headers': 'content-type'
    }

    if request.method == 'GET':
        id = request.query.get('id')
        try:
            if id:
                async with request.app['db'].acquire() as conn:
                    deposits = await db.get_deposit_by_id(conn=conn,deposit_id=id)
                    logging.debug(msg=f'deposits: {str(deposits)}')
                    return web.json_response(deposits, headers=headers)
            else:
                async with request.app['db'].acquire() as conn:
                    deposits = await db.get_deposits(conn=conn)
                    logging.debug(msg=f'deposits: {str(deposits)}')
                    return web.json_response({ 'deposits': deposits }, headers=headers)
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=headers)


async def metadata(request):
    headers = {
    'ACCESS-CONTROL-ALLOW-ORIGIN': '*',
    'Access-Control-Allow-Headers': 'content-type'
    }

    if request.method == 'GET':
        try:
            q = request.query
            fd = FormData()

            config = dict({'collection_name': 'deposits', "deposit_id": q.get('deposit_id')})
            fd.add_field('config', json.dumps(config), content_type='application/json')
            
            async with new_request(method='GET', url='http://mongo-service:5000/objects', data=fd) as resp:
                logging.debug("MONGO ERROR:"+await resp.text())
                resp_json = await resp.json()
                return web.json_response(resp_json, headers=headers)
        
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=headers)
