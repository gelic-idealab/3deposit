from sqlalchemy import create_engine, MetaData

from db import forms, deposits, users, services, actions
from settings import BASE_DIR, get_config
from security import generate_password_hash

import time


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres', password='postgres', database='postgres',
    host='postgres', port=5432
)

admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')

USER_CONFIG_PATH = BASE_DIR / 'gateway' / 'db_config.yml'
USER_CONFIG = get_config(['-c', USER_CONFIG_PATH.as_posix()])
USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
user_engine = create_engine(USER_DB_URL)


def setup_db(config):

    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))
    conn.close()


def teardown_db(config):

    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("""
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = '%s'
        AND pid <> pg_backend_pid();""" % db_name)
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[forms, deposits, users, services, actions])


def drop_tables(engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[forms, deposits, users, services])

def create_admin(engine):
    username = 'admin'
    password_hash = generate_password_hash('admin')
    role = 'admin'
    with engine.connect() as conn:
        conn.execute(users.insert().values(username=username, password_hash=password_hash, role=role))

def create_default_store_service(engine):
    action = 'store'
    media_type = 'default'
    service_name = 'minio'
    with engine.connect() as conn:
        conn.execute(actions.insert().values(action=action, media_type=media_type, service_name=service_name))

def main():
    # time.sleep(5)
    setup_db(USER_CONFIG['postgres'])
    create_tables(engine=user_engine)
    create_admin(engine=user_engine)
    create_default_store_service(engine=user_engine)
    # drop_tables()
    # teardown_db(config)

if __name__ == '__main__':
    main()