import os
# import json
# import datetime
import logging
import aiopg.sa
from security import generate_password_hash
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime, Boolean, JSON,
    and_
)

__all__ = ['forms', 'deposits', 'users', 'services', 'actions']

meta = MetaData()
deposits = Table(
    'deposits', meta,

    Column('deposit_id', String(256), primary_key=True),
    Column('deposit_date', Integer),
    Column('etag', String(256)),
    Column('mongo_id', String(256)),
    Column('resource_id', String(256)),
    Column('media_type', String(256))
)

forms = Table(
    'forms', meta,

    Column('id', String(256), primary_key=True),
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


# Application database init & teardown
async def init_pg(app):

    user_username = os.environ.get('POSTGRES_USER')
    user_password = os.environ.get('POSTGRES_PASSWORD')
    user_database = os.environ.get('POSTGRES_DB')
    user_host = 'postgres'
    user_port = '5432'
    engine = await aiopg.sa.create_engine(
        database=user_database,
        user=user_username,
        password=user_password,
        host=user_host,
        port=user_port,
        minsize=1,
        maxsize=5
    )
    app['db'] = engine
    return engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


# Deposit queries
async def add_deposit_by_id(conn, deposit_id):
    logging.debug(msg=f'add_deposit_by_id id: {deposit_id}')
    await conn.execute(
        deposits
        .insert()
        .values(deposit_id=deposit_id)
    )


async def update_deposit_by_id(conn, deposit_id, **kwargs):
    logging.debug(f'kwargs passed to update_deposit_id {deposit_id}: {kwargs}')
    result = await conn.execute(
        deposits
        .update()
        .where(deposits.c.deposit_id == deposit_id)
        .values(kwargs)
    )


async def get_deposits(conn):
    result = await conn.execute(
        deposits
        .select().order_by(deposits.c.deposit_date.desc())
    )

    deposit_list = await result.fetchall()
    if deposit_list:
        column_keys = result.keys()
        deposit_objects = []
        for d in deposit_list:
            d_obj = {}
            for (i, k) in enumerate(column_keys):
                d_obj.update(dict({k: str(d[i])}))
            deposit_objects.append(d_obj)
        return deposit_objects
    else:
        return None


async def get_deposit_by_id(conn, deposit_id):
    result = await conn.execute(
        deposits
        .select()
        .where(deposits.c.deposit_id == deposit_id))
    deposit_record = await result.first()
    if not deposit_record:
        return None

    d_obj = {}
    for (i, k) in enumerate(deposit_record.keys()):
        d_obj.update(dict({k: str(deposit_record[i])}))
    return d_obj


# User queries
async def get_users(conn):
    result = await conn.execute(
        users.select().order_by(users.c.id)
    )
    column_keys = result.keys()
    user_list = await result.fetchall()
    if user_list:
        user_objects = []
        for u in user_list:
            u_obj = {}
            for (i, k) in enumerate(column_keys):
                u_obj.update(dict({k: u[i]}))
            user_objects.append(u_obj)
        return user_objects
    else:
        return None


async def get_user_by_name(conn, username):
    result = await conn.execute(
        users
        .select()
        .where(users.c.username == username)
    )
    user_record = await result.first()
    return user_record


async def update_user(conn, user):
    result = await conn.execute(
        users
        .update()
        .where(users.c.username == user.get('username'))
        .values(role=user.get('role'), email=user.get('email'))
    )
    return True

async def create_user(conn, username, password, email, role='user'):
    password_hash = generate_password_hash(password)
    result = await conn.execute(
        users
        .insert()
        .values(username=username, password_hash=password_hash, email=email, role=role)
    )
    user = await result.first()
    return dict(user)


async def delete_user(conn, username):
    result = await conn.execute(
        users
        .delete()
        .where(users.c.username == username)
    )
    return result


# Form queries
async def get_forms(conn):
    result = await conn.execute(
        forms
        .select().order_by(forms.c.id)
    )
    forms_result = await result.fetchall()
    return [form.id for form in forms_result]


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


async def create_form(conn, id, content):
    await conn.execute(
        forms
        .insert()
        .values(id=id, content=content)
    )
    return True


async def update_form_by_id(conn, id, content):
    result = await conn.execute(
        forms
        .update()
        .where(forms.c.id == id)
        .values(content=content)
    )
    if result.rowcount > 0:
        return True
    else:
        created = await create_form(conn, id, content)
        return created


# Service queries
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
            for (i, k) in enumerate(column_keys):
                s_obj.update(dict({k: s[i]}))
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


# Action queries
async def delete_action_service_name(conn, action, media_type, service_name):
    logging.debug(msg='delete_action_service_name called with: {}, {}, {}'.format(action, media_type, service_name))
    result = await conn.execute(
        actions
        .delete()
        .where(
            and_(
                    actions.c.action == action,
                    actions.c.media_type == media_type,
                    actions.c.service_name == service_name
                )
            )
        )
    service = await result.fetchone()
    logging.debug(msg='delete_action_service_name fetchone: {}'.format(str(service)))
    if service:
        logging.debug(msg='action service deleted: {}'.format(str(dict(service))))
        service_name = service.get('service_name')
        return str(service_name)
    else:
        return None


async def get_action_service_name(conn, action, media_type='default'):
    logging.debug(msg='get_action_service_name called with: {}, {}'.format(action, media_type))
    result = await conn.execute(
        actions
        .select()
        .where(
            and_(
                actions.c.action == action,
                actions.c.media_type == media_type,
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


async def set_action_service_name(conn, action, media_type, service_name):
    logging.debug(msg='set_action_service_name called with: {}, {}: {}'.format(action, media_type, service_name))
    current_service = await get_action_service_name(conn, action, service_name, media_type)
    if current_service:
        await conn.execute(
            actions
            .update()
            .where(
                    and_(
                        actions.c.action == action,
                        actions.c.media_type == media_type
                    )
                )
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
            for (i, k) in enumerate(column_keys):
                s_obj.update(dict({k:s[i]}))
            service_objects.append(s_obj)
        return service_objects
    else:
        return None
