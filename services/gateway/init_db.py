import time
import logging
import os
import json

from sqlalchemy import create_engine, MetaData

from db import forms, deposits, users, services, actions
from settings import BASE_DIR, get_config
from security import generate_password_hash


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

ADMIN_DB_URL = DSN.format(
    user='postgres',
    password=os.environ.get('PG_ADMIN_PASSWORD'), 
    database='postgres',
    host='postgres', 
    port=5432
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


# def teardown_db(config):

#     db_name = config['database']
#     db_user = config['user']

#     conn = admin_engine.connect()
#     conn.execute("""
#       SELECT pg_terminate_backend(pg_stat_activity.pid)
#       FROM pg_stat_activity
#       WHERE pg_stat_activity.datname = '%s'
#         AND pid <> pg_backend_pid();""" % db_name)
#     conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
#     conn.execute("DROP ROLE IF EXISTS %s" % db_user)
#     conn.close()


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[forms, deposits, users, services, actions])


# def drop_tables(engine):
#     meta = MetaData()
#     meta.drop_all(bind=engine, tables=[forms, deposits, users, services, actions])


def create_admin(engine):
    username = os.environ.get('3DEPOSIT_ADMIN_USERNAME')
    password_hash = generate_password_hash(os.environ.get('3DEPOSIT_ADMIN_PASSWORD'))
    role = 'admin'
    email = os.environ.get('3DEPOSIT_ADMIN_EMAIL')
    with engine.connect() as conn:
        conn.execute(users.insert().values(username=username, password_hash=password_hash, role=role, email=email))

def create_default_actions(engine):
    with engine.connect() as conn:
        objects = [
            {
                'action': 'publish',
                'media_type': 'video',
                'service_name': 'vimeo'
            },
            {
                'action': 'publish',
                'media_type': 'model',
                'service_name': 'sketchfab'
            },
            {
                'action': 'store',
                'media_type': 'default',
                'service_name': 'minio'
            },
            {
                'action': 'publish',
                'media_type': 'vr',
                'service_name': 'aws'
            }
        ]

        for obj in objects:
            conn.execute(actions.insert().values(action=obj.get('action'), media_type=obj.get('media_type'), service_name=obj.get('service_name')))


def create_default_services(engine):
    env = os.environ
    with engine.connect() as conn:
        objects = [
            {
                'name': 'minio',
                "endpoint": 'http://minio-service:5000',
                'config': {
                    "auth": {
                        "access_key": env.get('MINIO_ACCESS_KEY'), 
                        "secret_key": env.get('MINIO_SECRET_KEY')
                    }
                }
            },
            {
                'name': 'sketchfab',
                "endpoint": 'http://sketchfab-service:5000',
                'config': {
                    "auth": {
                        "token": env.get('SKETCHFAB_TOKEN')
                    }
                }
            },
            {
                'name': 'vimeo',
                "endpoint": 'http://vimeo-service:5000',
                'config': {
                    "auth": {
                        "client_id": env.get('VIMEO_CLIENT_ID'), 
                        "access_token": env.get('VIMEO_ACCESS_TOKEN'), 
                        "client_secret": env.get('VIMEO_CLIENT_SECRET')
                    }
                }
            },
            {
                'name': 'aws',
                "endpoint": 'http://aws-service:5000',
                'config': {
                    "bucket_name": env.get('AWS_BUCKET_NAME'), 
                    "auth": {
                        "access_key": env.get('AWS_ACCESS_KEY'), 
                        "secret_key": env.get('AWS_SECRET_KEY')
                    }
                }
            }
        ]

        for obj in objects:
            conn.execute(services.insert().values(name=obj.get('name'), endpoint=obj.get('endpoint'), config=obj.get('config')))


def main():
    setup_db(USER_CONFIG['postgres'])
    # create_tables(engine=user_engine) 
    create_admin(engine=user_engine)
    create_default_actions(engine=user_engine)
    create_default_services(engine=user_engine)
    # drop_tables()
    # teardown_db(config)


if __name__ == '__main__':
    main()
