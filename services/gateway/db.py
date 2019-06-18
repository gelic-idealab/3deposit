import json
import logging
import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, Boolean, JSON
)

__all__ = ['forms', 'deposits', 'users', 'services', 'actions']

meta = MetaData()

deposits = Table(
    'deposits', meta,

    Column('id', Integer, primary_key=True),
    Column('deposit_date', Date, nullable=False),
    Column('etag', String(256), nullable=False),
    Column('mongo_id', String(256), nullable=False),
    Column('location', String(256), nullable=True)
)

forms = Table(
    'forms', meta,

    Column('id', Integer, primary_key=True),
    Column('active', Boolean, nullable=False, default=False),
    Column('content', JSON, nullable=True)
)

users = Table(
    'users', meta,

    Column('id', Integer, primary_key=True),
    Column('username', String(64), nullable=False, unique=True),
    Column('email', String(128)),
    Column('password_hash', String(128), nullable=False),
    Column('role', String(64), nullable=False)
)

services = Table(
    'services', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(128), nullable=False),
    Column('endpoint', String(256), nullable=False),
    Column('config', JSON, nullable=True)
)

actions = Table(
    'actions', meta,

    Column('id', Integer, primary_key=True),
    Column('action', String(128), nullable=False),
    Column('media_type', String(128), nullable=False),
    Column('service_name', String(128), nullable=False)
)

class RecordNotFound(Exception):
    """Requested record in database was not found"""


### Database init & teardown
async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine
    return engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


### Deposit queries
async def get_deposit_by_id(conn, deposit_id):
    result = await conn.execute(
        deposits
        .select()
        .where(deposits.c.id == deposit_id))
    deposit_record = await result.first()
    if not deposit_record:
        msg = "Deposit with id: {} not found"
        raise RecordNotFound(msg.format(deposit_id))
    return deposit_record


### User queries
async def get_users(conn):
    records = await conn.execute(
        users.select().order_by(users.c.id)
    )
    return records

async def get_user_by_name(conn, username):
    result = await conn.execute(
        users
        .select()
        .where(users.c.username == username)
    )
    user_record = await result.first()
    return user_record

    


### Deposit form queries
async def get_active_form(conn):
    result = await conn.execute(
        forms
        .select()
        .where(forms.c.active == True)
    )
    first_active_form = await result.fetchone()
    if first_active_form:
        return dict(first_active_form)
    else:
        return None

async def create_active_form(conn, content, active=False):
    await conn.execute(
        forms
        .insert()
        .values(active=active, content=content)
    )


### Service config queries
async def get_services(conn):
    result = await conn.execute(
        services
        .select()
    )
    column_keys = result.keys()
    service_list = await result.fetchall()
    if service_list:
        service_objects = []
        for s in service_list:
            s_obj = {}
            for (i,k) in enumerate(column_keys):
                s_obj.update(dict({k:s[i]}))
            service_objects.append(s_obj)
        return service_objects
    else:
        return None

async def get_service_config(conn, name):
    result = await conn.execute(
        services
        .select()
        .where(services.c.name == name)
    )
    service = await result.fetchone()
    logging.debug(msg='get_service_config returned: {}'.format(str(service)))
    if service:
        return dict(service)
    else:
        return None

async def set_service_config(conn, name, endpoint, config):
    service = await get_service_config(conn, name)
    if service:
        await conn.execute(
            services
            .update()
            .where(services.c.name == name)
            .values(endpoint=endpoint, config=config)
        )
        return 'service config updated for {}'.format(name)
    else:
        await conn.execute(
            services
            .insert()
            .values(name=name, endpoint=endpoint, config=config)
        )
        return 'service config created for {}'.format(name)

# action config queries
async def get_action_service_name(conn, action, media_type):
    logging.debug(msg='get_action_service_name called with: {}, {}'.format(action, media_type))
    result = await conn.execute(
        actions
        .select()
        .where(actions.c.action == action)
        # .where(actions.c.media_type == media_type)
        )
    service = await result.fetchone()
    service_dict = dict(service)
    service_name = service_dict.get('service_name')
    logging.debug(msg='service name retrieved: {}'.format(str(service_name)))
    if service_name:
        return str(service_name)
    else:
        return None

async def get_action_services(conn):
    result = await conn.execute(
        actions
        .select()
    )
    column_keys = result.keys()
    service_list = await result.fetchall()
    if service_list:
        service_objects = []
        for s in service_list:
            s_obj = {}
            for (i,k) in enumerate(column_keys):
                s_obj.update(dict({k:s[i]}))
            service_objects.append(s_obj)
        return service_objects
    else:
        return None