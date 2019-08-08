import os
import time
import logging
import sys
import base64
import jinja2
from cryptography import fernet
from psycopg2 import OperationalError

import uvloop
from aiohttp import web
import aiohttp_jinja2
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import authorized_userid
from aiohttp_security import setup as setup_security
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from db import close_pg, init_pg
from settings import get_config, PACKAGE_NAME
from auth import DBAuthorizationPolicy
from routes import setup_routes


async def current_user_ctx_processor(request):
    username = await authorized_userid(request)
    is_anonymous = not bool(username)
    return {'current_user': {'is_anonymous': is_anonymous}}


async def init_app(argv=None):

    app = web.Application(client_max_size=10*1024*1024) # max client payload of 10MB

    app['config'] = get_config(argv)

    # create db connection on startup, close on exit
    # app.on_startup.append(init_pg)
    try:
        db_pool = await init_pg(app)
        app.on_cleanup.append(close_pg)
    except Exception as err:
        logging.debug(msg=err)
        raise

    # use key to sign cookie
    env_key = base64.urlsafe_b64encode(bytes(os.environ.get('3DEPOSIT_SECRET_KEY'), 'utf-8'))
    secret_key = base64.urlsafe_b64decode(env_key)
    setup_session(app, EncryptedCookieStorage(secret_key))

    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader(PACKAGE_NAME),
        context_processors=[current_user_ctx_processor],
    )

    setup_security(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(db_pool)
    )

    # setup views and routes
    setup_routes(app)

    # logging
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.basicConfig(level=logging.DEBUG, filename='./data/gateway.log')

    return app


def main(argv):

    # init & run app with args & config
    app = init_app(argv)
    config = get_config(argv)
    web.run_app(app,
                host=config['host'],
                port=config['port'])


if __name__ == '__main__':
    main(sys.argv[1:])
