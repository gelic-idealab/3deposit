import json

import aiohttp_jinja2
from aiohttp import web, ClientSession, FormData
from aiohttp_security import remember, forget, authorized_userid

import db
from forms import validate_login_form


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
API endpoint for frontend to request active deposit form

'GET': no params; returns first active form as object { 'active_form': {<form>} }
'POST': creates new form from raw request body 'request.json()'
"""

async def active_deposit_form(request):
    if request.method == 'GET':
        async with request.app['db'].acquire() as conn:
            active_form = await db.get_active_form(conn)
        if active_form:
            return web.json_response({ 'active_form': active_form }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
        else:
            return web.json_response({ 'err': 'No active form' }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))

    if request.method == 'POST':
        try:
            req = await request.json()
            async with request.app['db'].acquire() as conn:
                try:
                    await db.create_active_form(conn, req['content'], req['active'])
                    return web.json_response({ "succeeded": True, "msg": "New active form created" })
                except Exception as e:
                    return web.json_response({ "err": str(e) })
        except Exception as e:
            return web.json_response({ "err": str(e) })


"""
API endpoint for frontend to upload files with support for chunking
'POST': only allowed method
"""

async def upload_file(request):
    if request.method == 'POST':
        try:
            req = await request.read()
            return web.Response(text=str(req), headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
        except Exception as err:
            return web.json_response({ 'err': str(err) }, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))
    else:
        return web.Response(status=200, headers=({'ACCESS-CONTROL-ALLOW-ORIGIN': '*'}))     

"""
Relay endpoint to make object storage calls
Endpoints are scoped for objects and buckets
"""
SERVICE_ENDPOINT = 'http://minio-service:5000/bucket'

async def minio_buckets(request):
    async with ClientSession() as session:    
        if request.method == 'GET':
            try:
                # construct form data
                req = await request.json()
                async with session.get(SERVICE_ENDPOINT, json=req) as resp:
                    try:
                        resp_json = await resp.json()
                    except Exception as err:
                        return web.json_response({'err': str(err), 'resp': await resp.text()})
                    return web.json_response({ 'resp': resp_json, 'req': req })
            except Exception as err:
                return web.json_response({ 'origin': 'gateway', 'err': str(err), 'req': req })

        if request.method == 'POST':
            try:
                req = await request.json()
                async with session.post(SERVICE_ENDPOINT, json=req) as resp:
                    resp_json = await resp.json()
                    return web.json_response({ 'resp': resp_json, 'req': req })
            except Exception as err:
                return web.json_response({ 'origin': 'gateway', 'err': str(err) })


"""
Handler for getting and setting services & service configs
"""

async def services(request):
    if request.method == 'GET':
        try:
            async with request.app['db'].acquire() as conn:
                services = await db.get_services(conn)
                if services:
                    return web.json_response({ 'services': services })
                else:
                    return web.json_response({ 'res': 'no services'})
        except Exception as err:
            return web.json_response({ 'err': str(err) })

async def services_configs(request):
    if request.method == 'GET':
        try:
            req = await request.json()
            async with request.app['db'].acquire() as conn:
                service_config = await db.get_service_config(conn, req.get('name'))
                if service_config:
                    return web.json_response({ service_config })
                else:
                    return web.json_response({ 'err': 'No matching service', 'req': req })
        except Exception as err:
            return web.json_response({ 'err': str(err), 'req': req })
    if request.method == 'POST':
        try:
            req = await request.json()
            async with request.app['db'].acquire() as conn:
                service = await db.set_service_config(conn, req.get('name'), req.get('config'))
                if service:
                    return web.json_response({ 'res': service })
        except Exception as err:
            return web.json_response({ 'err': str(err), 'req': req })


"""
Helper function to relay form data with files
"""
async def handle(request):
    fd = FormData()
    auth = json.dumps({'auth': {'auth_key': 'auth_value'}})
    data = json.dumps({'deposit_id': '12345'})
    fd.add_field('config', auth, content_type='application/json')
    fd.add_field('data', data, content_type='application/json')
    fd.add_field('files', open('test.txt', 'rb'), filename='test.txt')
    async with ClientSession() as session:
        async with session.post(SERVICE_ENDPOINT, data=fd) as resp:
            return web.json_response({"res": await resp.json() })
