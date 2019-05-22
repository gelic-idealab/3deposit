import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date
)

__all__ = ['deposits', 'users']

meta = MetaData()

deposits = Table(
    'deposits', meta,

    Column('deposit_id', Integer, primary_key=True),
    Column('deposit_date', Date, nullable=False),
    Column('etag', String(256), nullable=False),
    Column('mongo_id', String(256), nullable=False),
    Column('location', String(256), nullable=True)
)

forms = Table(
    'forms', meta,

    Column('form_id', Integer, primary_key=True),
    Column('active', bool, nullable=False, default=False),
    Column('content', String(1024), nullable=True)
)

users = Table(
    'users', meta,

    Column('id', Integer, primary_key=True),
    Column('username', String(64), nullable=False, unique=True),
    Column('email', String(128)),
    Column('password_hash', String(128), nullable=False),
    Column('role', String(64), nullable=False)
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""


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


async def get_deposit_by_id(conn, deposit_id):
    result = await conn.execute(
        deposits.select()
        .where(deposits.c.id == deposit_id))
    deposit_record = await result.first()
    if not deposit_record:
        msg = "Deposit with id: {} not found"
        raise RecordNotFound(msg.format(deposit_id))
    return deposit_record

async def get_user_by_name(conn, username):
    result = await conn.execute(
        users
        .select()
        .where(users.c.username == username)
    )
    user_record = await result.first()
    return user_record

async def get_active_form(conn):
    result = await conn.execute(
        forms
        .select()
        .where(forms.c.active == True)
    )
    active_form = result.first()
    return active_form

async def get_users(conn):
    records = await conn.execute(
        users.select().order_by(users.c.id)
    )
    return records
    