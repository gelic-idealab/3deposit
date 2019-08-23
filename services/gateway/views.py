import json
import logging
import os
import logging
from datetime import datetime
from asyncio import create_task

import db
import aiohttp_jinja2
from aiohttp import web, FormData, ClientSession
from aiohttp import request as new_request
from aiohttp_security import remember, forget, authorized_userid

from forms import validate_login_form, validate_new_user_form
from process import get_service_config_by_action, start_deposit_processing_task


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
        return web.HTTPFound('/admin/')

    if request.method == 'POST':
        form = await request.post()

        async with request.app['db'].acquire() as conn:
            error = await validate_login_form(conn, form)

            if error:
                return {'error': error}
            else:
                response = web.HTTPFound('/admin/')

                user = await db.get_user_by_name(conn, form['username'])
                await remember(request, response, user['username'])

                return response

    return {}

async def logout(request):
    response = redirect(request.app.router, 'login')
    await forget(request, response)
    return response


@aiohttp_jinja2.template('signup.html')
async def signup(request):
    # username = await authorized_userid(request)
    # if not username:
    #     raise web.HTTPUnauthorized()
    token = request.query.get('token')
    env_token = os.environ.get('3DEPOSIT_SIGNUP_TOKEN')
    if token != env_token:
        raise web.HTTPUnauthorized()
    
    else:
    # async with request.app['db'].acquire() as conn:
    #     current_user = dict(await db.get_user_by_name(conn, username))
    #     if current_user.get('role') != 'admin':
    #         raise web.HTTPUnauthorized()
        if request.method == 'POST':
            form = await request.post()

            async with request.app['db'].acquire() as conn:
                error = await validate_new_user_form(conn, form)

                if error:
                    return {'error': error, 'token': token}
                else:
                    username = form.get('username')
                    password = form.get('password')
                    email = form.get('email')
                    user = await db.create_user(conn=conn, username=username, password=password, email=email)
                    logging.info(msg=f'User created: {str(user)}')
                    return web.HTTPFound('login')

    return {'token': token}



async def current_user(request):
    username = await authorized_userid(request)
    if not username:
        raise web.HTTPUnauthorized()

    async with request.app['db'].acquire() as conn:
        current_user = await db.get_user_by_name(conn, username)

    return web.json_response({'current_user': dict(current_user)})

async def users(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        if not username:
            raise web.HTTPUnauthorized()
        current_user = dict(await db.get_user_by_name(conn, username))
        if current_user.get('role') != 'admin':
            raise web.HTTPUnauthorized()
    
    if request.method == 'GET':
        async with request.app['db'].acquire() as conn:
            users = await db.get_users(conn)

        return web.json_response({'users': users})
    
    if request.method == 'DELETE':
        data = await request.json()
        user_to_delete = data.get('username')
        async with request.app['db'].acquire() as conn:
            deleted = await db.delete_user(conn, user_to_delete)
        return web.json_response({'deleted': str(deleted)})


"""
Handlers for getting and setting services & service configs
"""


async def services(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        if not username:
            raise web.HTTPUnauthorized()
        current_user = dict(await db.get_user_by_name(conn, username))
        if current_user.get('role') != 'admin':
            raise web.HTTPUnauthorized()

    if request.method == 'GET':
        try:
            async with request.app['db'].acquire() as conn:
                services = await db.get_services(conn)
                if services:
                    return web.json_response({'services': services})
                else:
                    return web.json_response({'res': 'no services'})
        except Exception as err:
            return web.json_response({'err': str(err)})
    else:
        return web.Response()


async def services_configs(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        if not username:
            raise web.HTTPUnauthorized()
        current_user = dict(await db.get_user_by_name(conn, username))
        if current_user.get('role') != 'admin':
            raise web.HTTPUnauthorized()
    headers = {
        'Access-Control-Allow-Headers': 'content-type'
    }
    if request.method == 'GET':
        try:
            req = request.query
            async with request.app['db'].acquire() as conn:
                service_config = await db.get_service_config(conn=conn, name=req.get('name'))
                if service_config:
                    return web.json_response({'service_config': service_config}, headers=headers)
                else:
                    return web.json_response({'err': 'No matching service', 'req': req}, headers=headers)
        except Exception as err:
            return web.json_response({'err': str(err), 'req': req}, headers=headers)
    elif request.method == 'POST':
        try:
            req = await request.json()
            async with request.app['db'].acquire() as conn:
                service = await db.set_service_config(conn=conn, name=req.get('name'), endpoint=req.get('endpoint'), config=req.get('config'))
                if service:
                    return web.json_response({'res': service}, headers=headers)
                else:
                    return web.json_response({'req': str(req), 'err': 'Could not create service.'}, headers=headers)
        except Exception as err:
            return web.json_response({'err': str(err)}, headers=headers)

    else:
        return web.Response(headers=headers)


async def services_actions(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        if not username:
            raise web.HTTPUnauthorized()
        current_user = dict(await db.get_user_by_name(conn, username))
        if current_user.get('role') != 'admin':
            raise web.HTTPUnauthorized()
    if request.method == 'GET':
        try:
            q = request.query
            action = q.get('action')
            media_type = q.get('media_type')
            if q:
                async with request.app['db'].acquire() as conn:
                    service_name = await db.get_action_service_name(conn, action=action, media_type=media_type)
                    if service_name:
                        return web.json_response({'service_name': service_name})
                    else:
                        return web.json_response(
                            {'res': 'no service configured for {}, {}'.format(action, media_type)}
                        )

            async with request.app['db'].acquire() as conn:
                services = await db.get_action_services(conn)
                if services:
                    return web.json_response({'services': services})
                else:
                    return web.json_response({'res': 'no action services'})
        except Exception as err:
            return web.json_response({'err': str(err)})

    if request.method == 'POST':
        try:
            req = await request.json()
            async with request.app['db'].acquire() as conn:
                service = await db.set_action_service_name(
                    conn=conn,
                    action=req.get('action'), 
                    media_type=req.get('media_type'), 
                    service_name=req.get('service_name'))
                if service:
                    return web.json_response({'res': service})
        except Exception as err:
            return web.json_response({'err': str(err)})

    else:
        return web.Response(headers={
            'Access-Control-Allow-Headers': 'content-type'
        })

"""
Handlers for deposit form frontend
"""


async def deposit_form(request):
    if request.method == 'GET':
        form_id = request.query.get('form_id')
        async with request.app['db'].acquire() as conn:
            form = await db.get_form_by_id(conn, id=form_id)
        if form:
            return web.json_response({'form': form})
        else:
            return web.json_response({'err': f'No form with id {form_id}'})

    if request.method == 'POST':
        username = await authorized_userid(request)
        async with request.app['db'].acquire() as conn:
            if not username:
                raise web.HTTPUnauthorized()
            current_user = dict(await db.get_user_by_name(conn, username))
            if current_user.get('role') != 'admin':
                raise web.HTTPUnauthorized()
        try:
            req = await request.json()
            form_id = req.get('form_id')
            content = req.get('content')
            if form_id and content:
                try:
                    async with request.app['db'].acquire() as conn:
                        form = await db.update_form_by_id(conn, form_id, content)
                        return web.json_response({'msg': f'Updated content for form {form_id}: {form}'})
                except Exception as e:
                    return web.json_response({'err': str(e)})
            else:
                return web.json_response({'err': f'Missing params for req: {str(req)}'})
        except Exception as e:
            return web.json_response({'err': 'Error handling request: ' + str(e)})


async def deposit_upload(request):
    if request.method == 'POST':
        try:
            reader = await request.multipart()
            did = request.query['deposit_id']
            rcn = request.query['resumableChunkNumber']
            rtc = request.query['resumableTotalChunks']
            while True:
                part = await reader.next()
                if part is None:
                    break
                if part.name == 'file':
                    chunk_file = f'./data/{did}_{rcn}'
                    with open(chunk_file, 'wb') as f:
                        b = await part.read()
                        f.write(b)
                    if int(rcn) == int(rtc):
                        with open(f'./data/{did}', 'wb') as f:
                            chunk_to_write = 1
                            while chunk_to_write <= int(rtc):
                                current_chunk = f'./data/{did}_{str(chunk_to_write)}'
                                with open(current_chunk, 'rb') as c:
                                    f.write(c.read())
                                    os.remove(current_chunk)
                                    chunk_to_write += 1


                    # if rcn == 1:
                    #     with open('./data/{}'.format(did+'_partial'), 'wb') as f:
                    #         b = await part.read()
                    #         f.write(b)
                    # elif rcn > 1:
                    #     with open('./data/{}'.format(did+'_partial'), 'ab') as f:
                    #         b = await part.read()
                    #         f.write(b)
                    # if rcn == rtc:
                    #     os.rename('./data/{}'.format(did+'_partial'), './data/{}'.format(did))
            return web.Response(status=200)
        except Exception as err:
            return web.json_response({'err': str(err)}, status=503)
    else:
        return web.Response(status=200)


async def deposit_submit(request):
    headers = {
        'Access-Control-Allow-Headers': 'content-type'
    }
    if request.method == 'POST':
        try:
            deposit_date = {'deposit_date': round(datetime.timestamp(datetime.now()))}
            data = await request.json()
            data.update(deposit_date)
            deposit_processed = create_task(start_deposit_processing_task(data))
            if deposit_processed:
                return web.Response(status=200, headers=headers)
            else:
                return web.Response(status=418, headers=headers)
        except Exception as err:
            return web.json_response({'err': str(err)}, headers=headers)
    else:
        return web.Response(status=200, headers=headers)


"""
Relay endpoint to make object storage calls
Endpoints are scoped for objects and buckets
"""


async def store_buckets(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        if not username:
            raise web.HTTPUnauthorized()
        current_user = dict(await db.get_user_by_name(conn, username))
        if current_user.get('role') != 'admin':
            raise web.HTTPUnauthorized()
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
                return web.json_response({'resp': resp_json})
        except Exception as err:
            return web.json_response({'origin': 'gateway', 'err': str(err)})

    if request.method == 'POST':
        try:
            data = await request.json()
            fd = FormData()
            fd.add_field('config', json.dumps(config), content_type='application/json')
            fd.add_field('data', json.dumps(data), content_type='application/json')
            # payload = dict({'config': config, 'data': data})
            async with new_request(method='POST', url=endpoint+PATH, data=fd) as resp:
                resp_json = await resp.json()
                return web.json_response({'resp': resp_json})
        except Exception as err:
            return web.json_response({'origin': 'gateway', 'err': str(err)})


async def store_objects(request):
    username = await authorized_userid(request)
    async with request.app['db'].acquire() as conn:
        if not username:
            raise web.HTTPUnauthorized()
        current_user = dict(await db.get_user_by_name(conn, username))
        if current_user.get('role') != 'admin':
            raise web.HTTPUnauthorized()
    PATH = '/object'
    async with request.app['db'].acquire() as conn:
        service_config = await get_service_config_by_action(conn=conn, action='store', media_type='default')
    config = dict(service_config.get('config'))
    endpoint = service_config.get('endpoint')
    bucket_name = dict({'bucket_name': '3deposit'})
    config.update(bucket_name)

    if request.method == 'GET':
        try:
            data = request.query
            config.update({'deposit_id': data.get('deposit_id')})
            fd = FormData()
            fd.add_field('config', json.dumps(config), content_type='application/json')
            async with new_request(method='GET', url=endpoint+PATH, data=fd) as resp:
                try:
                    resp_bin = await resp.read()
                except Exception as err:
                    return web.json_response({'err': str(err)})
                return web.Response(body=resp_bin)
        except Exception as err:
            return web.json_response({'err': str(err)})

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
            return web.json_response({'origin': 'gateway', 'err': str(err)})

    if request.method == 'DELETE':
        try:
            data = request.query
            config.update({'deposit_id': data.get('deposit_id')})
            fd = FormData()
            fd.add_field('config', json.dumps(config), content_type='application/json')

            # remove file from bucket
            async with new_request(method='DELETE', url=endpoint+PATH, data=fd) as resp:
                try:
                    resp_json = await resp.json()
                except Exception as err:
                    return web.json_response({'err': str(err)})
            
            # remove etag from mongo
            update = {
                'etag': 'DELETED'
            }

            config = {
                'deposit_id': data.get('deposit_id')
            }

            fd = FormData()
            fd.add_field('data', json.dumps(update), content_type='application/json')
            fd.add_field('config', json.dumps(config), content_type='application/json')

            async with new_request(method='PATCH', url='http://mongo-service:5000/objects', data=fd) as resp:
                resp_json.update(await resp.json())
                return web.json_response(resp_json)

        except Exception as err:
            return web.json_response({'err': str(err)})


"""
Relay endpoint to get/post to Model publication service
"""


async def publications(request):
    username = await authorized_userid(request)
    if not username:
        raise web.HTTPUnauthorized()
    headers = {
        'Access-Control-Allow-Headers': 'content-type'
    }

    try:
        q = request.query
        data = {
            'resource_id': q.get('resource_id')
        }

        media_type = q.get('media_type')

        async with request.app['db'].acquire() as conn:
            service_config = await get_service_config_by_action(conn=conn, action='publish', media_type=media_type)
        endpoint = service_config.get('endpoint')
        config = service_config.get('config')

        payload = {}
        payload.update({'data': json.dumps(data)})
        payload.update({'config': json.dumps(config)})

        async with new_request(method=request.method, url=endpoint, data=payload) as resp:
            return web.json_response(await resp.json(), headers=headers)

    except Exception as err:
        return web.json_response({"err": str(err)}, headers=headers)


async def deposits(request):
    username = await authorized_userid(request)
    if not username:
        raise web.HTTPUnauthorized()
    headers = {
        'Access-Control-Allow-Headers': 'content-type'
    }

    if request.method == 'GET':
        try:
            if request.query.get('deposit_id'):
                id = request.query.get('deposit_id')
                async with request.app['db'].acquire() as conn:
                    deposits = await db.get_deposit_by_id(conn=conn, deposit_id=id)
                    return web.json_response(deposits, headers=headers)

            else:
                async with request.app['db'].acquire() as conn:
                    deposits = await db.get_deposits(conn=conn)
                    return web.json_response(deposits, headers=headers)

        except Exception as err:
            return web.json_response({'err': str(err)}, headers=headers)


async def gallery(request):
    if request.method == 'GET':
        filters = None
        if request.query.get('filters'):
            filters = json.loads(request.query.get('filters'))

        fd = FormData()

        config = dict({"filters": filters})
        fd.add_field('config', json.dumps(config), content_type='application/json')

        async with new_request(method='GET', url='http://mongo-service:5000/objects', data=fd) as resp:
            resp_json = await resp.json()
            return web.json_response({'deposits': resp_json})


async def metadata(request):
    username = await authorized_userid(request)
    if not username:
        raise web.HTTPUnauthorized()

    if request.method == 'GET':
        try:
            q = request.query
            fd = FormData()

            config = dict({"deposit_id": q.get('deposit_id')})
            fd.add_field('config', json.dumps(config), content_type='application/json')

            async with new_request(method='GET', url='http://mongo-service:5000/objects', data=fd) as resp:
                resp_json = await resp.json()
                return web.json_response(resp_json)

        except Exception as err:
            return web.json_response({'err': str(err)})

    elif request.method == 'PATCH':
        try:
            q = request.query
            data = await request.json()

            fd = FormData()
            config = dict({"deposit_id": q.get('deposit_id')})

            fd.add_field('config', json.dumps(config), content_type='application/json')
            fd.add_field('data', json.dumps(data), content_type='application/json')            

            async with new_request(method='PATCH', url='http://mongo-service:5000/objects', data=fd) as resp:
                resp_json = await resp.json()
                return web.json_response(resp_json)

        except Exception as err:
            return web.json_response({'err': str(err)})


async def metadata_keys(request):
    username = await authorized_userid(request)
    if not username:
        raise web.HTTPUnauthorized()

    if request.method == 'GET':
        try:
            async with new_request(method='GET', url='http://mongo-service:5000/keys') as resp:
                resp_json = await resp.json()
                return web.json_response(resp_json)

        except Exception as err:
            return web.json_response({'err': str(err)})