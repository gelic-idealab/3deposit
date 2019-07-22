import os
import json
from json import JSONDecodeError
from flask import Flask, request, jsonify
from pymongo import MongoClient
from unpack.unpack import get_value
import logging
from bson import Code

DATABASE_NAME = '3deposit'
COLLECTION_NAME = 'deposits'


def create_client(request):
    if not request:
        return False

    username = 'root'
    password = 'example'

    client = MongoClient(f'mongodb://{username}:{password}@mongo-server:27017/')

    return client


def create_app():
    app = Flask(__name__)

    @app.route('/keys', methods=['GET'])
    def get_keys():
        client = create_client(request)
        database = client['3deposit']
        map = Code("function() { for (var key in this.deposit_metadata) { emit(key, null); } }")
        reduce = Code("function(key, stuff) { return null; }")
        result = database[COLLECTION_NAME].map_reduce(map, reduce, "metadata_keys")
        return jsonify({"keys": result.distinct('_id')})


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

                if deposit_id:
                    document = collection.find_one(filter={"deposit_id": deposit_id}, projection={'_id': False})    
                    return jsonify(document)

                if len(config.get('filters')) > 0:
                    filters = config.get('filters')
                    logging.debug(msg="FILTERS: "+str(filters))
                    where_clause = {}

                    for f in filters:
                        key = f['key']
                        op = f['op']
                        value = f['value']

                        op_dict = {
                            'Equals': '=',
                            'Excludes': '$ne',
                            'Between': 'between',
                            'Greater Than': '$gt',
                            'Less Than': '$lt',
                            'Contains': '~~*'
                        }

                        key = f'deposit_metadata.{key}'

                        op_dict_char = op_dict[op]
                        if op_dict_char == op_dict['Between']:
                            where_clause.update({key: {'$gte': value.split(',')[0], '$lte': value.split(',')[1]}})
                        elif op_dict_char == op_dict['Contains']:
                            where_clause.update({key: {'$regex': f'.*{value}.*'}})
                        elif op_dict_char in [op_dict['Excludes'], op_dict['Greater Than'], op_dict['Less Than']]:
                            where_clause.update({key: {op_dict_char: value}})
                        elif op_dict_char == op_dict['Equals']:
                            where_clause.update({key: value})

                    # logging.debug(msg=f'WHERE CLAUSE: {str(where_clause)}')
                    docs = collection.find(filter=where_clause, projection={'_id': False})
                    doc_list = []

                    for doc in docs:
                        doc_list.append(doc)

                    return jsonify(doc_list)

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
                return jsonify({"err": "Document not deleted."})

            # except Exception as err:
            #     return jsonify({"err": str(err)})

    return app
