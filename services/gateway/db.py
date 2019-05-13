import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date
)

__all__ = ['deposits', 'users']

meta = MetaData()

deposits = Table(
    'deposits', meta,

    Column('did', Integer, primary_key=True),
    Column('etag', String(200), nullable=False),
    Column('ddate', Date, nullable=False)
)

users = Table(
    'users', meta,

    Column('id', Integer, primary_key=True),
    Column('username', String(64), nullable=False, unique=True),
    Column('email', String(120)),
    Column('password_hash', String(128), nullable=False)
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


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def get_deposit_by_id(conn, deposit_id):
    result = await conn.execute(
        question.select()
        .where(deposits.c.id == deposit_id))
    deposit_record = await result.first()
    if not question_record:
        msg = "Deposit with id: {} not found"
        raise RecordNotFound(msg.format(deposit_id))
    return deposit_record

async def get_user_by_name(conn, username):
    result = await conn.fetchrow(
        users
        .select()
        .where(users.c.username == username)
    )
    return result


async def get_users(conn):
    records = await conn.fetch(
        users.select().order_by(users.c.id)
    )
    return records