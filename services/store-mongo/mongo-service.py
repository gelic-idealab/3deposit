import os
import json
from json import JSONDecodeError
from flask import Flask, request, jsonify
from pymongo import MongoClient
from unpack_001 import get_value
import logging

DATABASE_NAME = '3deposit'
COLLECTION_NAME = 'deposits'


def create_client(request):
    if not request:
        return False

    username = 'root'
    password = 'example'

    client = MongoClient(
        'mongodb://{username}:{password}@mongo-server:27017/'.format(
        username=username,
        password=password
        )
    )

    return client

def create_app():
    app = Flask(__name__)

    @app.route('/databases', methods=['GET', 'POST', 'DELETE'])
    def databases():
        # try:
        client = create_client(request)
        databases = client.list_database_names()
        return jsonify({"databases": databases})

        # except Exception as err:
        #     return jsonify({"err": str(err)})

    @app.route('/objects', methods=['GET', 'POST', 'DELETE'])
    def objects():
        if request.method == 'POST':
            # try:
            client = create_client(request)

            database = client['3deposit']

            # collection_name = get_value(request=request, scope='config', field='collection_name')
            # deposit_id = get_value(request=request, scope='data', field='deposit_id')

            logging.debug(msg=str(request.form))

            data = json.loads(request.form.get('data'))
            deposit_id = data.get('deposit_id')

            if not deposit_id:
                return jsonify({"err": "Please enter a valid deposit_id."})

            collection = database[COLLECTION_NAME]
            mongo_id = collection.insert_one(data).inserted_id
            if mongo_id:
                return jsonify({"mongo_id": str(mongo_id)})

            # except Exception as err:
            #     return jsonify({"err": str(err)})

        if request.method == 'GET':
            try:
                client = create_client(request)

                database = client[DATABASE_NAME]

                config = json.loads(request.form.get('config'))
                deposit_id = config.get('deposit_id')
                # logging.debug("COLLECTION NAME:"+collection_name)
                # JSONEncoder().encode()

                collection = database[COLLECTION_NAME]
                logging.debug(msg="MONGO GET COLLECTION: "+str(collection))
                logging.debug(msg="MONGO GET COLLECTION: "+str(dir(collection)))
                                
                document = collection.find_one(filter={"deposit_id": deposit_id}, projection={'_id': False})
                # deposit_metadata = document.get('deposit_metadata')

                return jsonify(document)

            except Exception as err:
                return jsonify({"err": str(err)})

        if request.method == 'DELETE':
            # try:
            client = create_client(request)

            database = client['3deposit']

            deposit_id = get_value(request=request, scope='data', field='deposit_id')
            collection_name = get_value(request=request, scope='config', field='collection_name')

            collection = database[collection_name]

            del_obj = collection.delete_one({"deposit_id": deposit_id})

            if del_obj:
                return jsonify({"del_obj": deposit_id})
            else:
                return jsonify({"err":"Document not deleted."})

            # except Exception as err:
            #     return jsonify({"err": str(err)})


    return app