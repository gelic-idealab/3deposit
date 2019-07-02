import json
import datetime
import logging
import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, Boolean, JSON,
    and_
)

from settings import BASE_DIR, get_config



__all__ = ['forms', 'deposits', 'users', 'services', 'actions']

meta = MetaData()

deposits = Table(
    'deposits', meta,

    Column('id', String(256), primary_key=True),
    Column('deposit_date', Date, nullable=False),
    Column('etag', String(256)),
    Column('mongo_id', String(256)),
    Column('location', String(256))
)

forms = Table(
    'forms', meta,

    Column('id', Integer, primary_key=True),
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



### Application database init & teardown
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
async def add_deposit_by_id(conn, deposit_id):
    logging.debug(msg=f'add_deposit_by_id id: {deposit_id}')
    await conn.execute(
        deposits
        .insert()
        .values(id=deposit_id, deposit_date=datetime.datetime.now())
    )

async def update_deposit_by_id(conn, deposit_id, **kwargs):
    logging.debug(f'kwargs passed to update_deposit_id {deposit_id}: {kwargs}')
    await conn.execute(
        deposits
        .update()
        .where(deposits.c.id == deposit_id)
        .values(kwargs)
    )

async def get_deposits(conn):
    result = await conn.execute(
        deposits
        .select()
    )
    deposit_list = await result.fetchall()
    if deposit_list:
        column_keys = result.keys()
        deposit_objects = []
        for d in deposit_list:
            d_obj = {}
            for (i,k) in enumerate(column_keys):
                d_obj.update(dict({k:str(d[i])}))
            deposit_objects.append(d_obj)
        return deposit_objects
    else:
        return None

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
async def get_form_by_id(conn, id):
    result = await conn.execute(
        forms
        .select()
        .where(forms.c.id == id)
    )
    form = await result.fetchone()
    if form:
        return dict(form)
    else:
        return None

async def create_form(conn, content):
    await conn.execute(
        forms
        .insert()
        .values(content=content)
    )

async def update_form_by_id(conn, id, content):
    await conn.execute(
        forms
        .update()
        .where(forms.c.id == id)
        .values(content=content)
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
    if service:
        logging.debug(msg='get_service_config returned: {}'.format(str(dict(service))))
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
async def get_action_service_name(conn, action, media_type='default'):
    logging.debug(msg='get_action_service_name called with: {}, {}'.format(action, media_type))
    result = await conn.execute(
        actions
        .select()
        .where(
            and_(
                actions.c.action == action,
                actions.c.media_type == media_type
                )
            )
        )
    service = await result.fetchone()
    logging.debug(msg='service fetchone: {}'.format(str(service)))
    if service:
        logging.debug(msg='service name retrieved: {}'.format(str(dict(service))))
        service_name = service.get('service_name')
        return str(service_name)
    else:
        return None

# action config queries
async def set_action_service_name(conn, action, media_type, service_name):
    logging.debug(msg='set_action_service_name called with: {}, {}: {}'.format(action, media_type, service_name))
    current_service = await get_action_service_name(conn, action, media_type)
    if current_service:
        await conn.execute(
            actions
            .update()
            .where(actions.c.action == action)
            # .where(actions.c.media_type == media_type)
            .values(service_name=service_name)
        )
        return 'action config updated for {}, {}: {}'.format(action, media_type, service_name)
    else:
        await conn.execute(
            actions
            .insert()
            .values(action=action, media_type=media_type, service_name=service_name)
        )
        return 'action config created for {}, {}: {}'.format(action, media_type, service_name)

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

