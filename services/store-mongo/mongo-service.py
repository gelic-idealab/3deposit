import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

import unpack

# https://api.mongodb.com/python/current/tutorial.html

DATABASE_NAME = '3deposit'

def mongo_keys(request_auth):
    if not request_auth:
        return False

    # config = json.loads(request_auth.form.get('config'))
    # auth = config.get('auth')

    try:
        # config = json.loads(request_auth.form.get('config'))
        access_key = get_value(request=request, scope='config', field='access_key')
        secret_key = get_value(request=request, scope='config', field='secret_key')

        auth_packed = {"access_key":access_key, "secret_key":secret_key}
        return auth_packed

    except JSONDecodeError as err:
        return {"err":"Invalid formatting of data.",
                        "log":str(err)}
    except (InvalidAccessKeyId,SignatureDoesNotMatch,AccessDenied) as err:
        return {"err":"Invalid Authentication.",
                        "log":str(err)}
    except AttributeError as err:
        return {"err":"Please provide auth keys.",
                        "log":str(err)}


def create_client(request):
    if not request:
        return False

    #COLLECTION_NAME = 'metadata'
    username = 'root'
    password = 'example'
    
    # database = client.DATABASE_NAME
    #collection = database.COLLECTION_NAME

    #try:
    minioClient = ''
    remote = get_value(request=request, scope='config', field='remote')
    region = None
    server_endpoint = 'err'

    if mongo_keys(request):
        auth = mongo_keys(request)
        if "err" in auth:
            return auth
    else:
        return {"err": "No authentication keys provided",
                        "log":str(err)}

    client = MongoClient(
        'mongodb://{username}:{password}@localhost:27017/'.format(
        username=username,
        password=password
        )
    )

    if server_endpoint == 'err':
        return {"err":"Please enter a valid provider."}

    return client
    
def create_app():
    app = Flask(__name__)

    @app.route('/databases', methods=['GET', 'POST', 'DELETE'])
    def databases():
        try:
            databases = client.list_database_names()
            return jsonify({"databases": databases})
        except Exception as err:
            return jsonify({"err": str(err)})

    # TO DO: Add Get, Post, and Delete request methods above

    @app.route('/objects', methods=['GET', 'POST', 'DELETE'])
    def objects():
        if request.method == 'POST':
            try:
                client = create_client(request)

                database = client.DATABASE_NAME

                collection = get_value(request=request, scope='config', field='collection')
                deposit_id = get_value(request=request, scope='data', field='deposit_id')
                
                data = json.loads(request.form.get('data'))
                deposit_metadata = data.get('deposit_metadata')

                if not collection:
                    return jsonify({"err":"Please enter a valid collection."})

                if not deposit_id:
                    return jsonify({"err":"Please enter a valid deposit_id."})

                # extract file & temp save to disk
                # file = request.files['file']
                # file.save(deposit_id)

                posts = database.posts
                post_id = posts.insert_one(deposit_metadata).inserted_id
                return jsonify({"post_id": str(post_id)})

            except Exception as err:
                return jsonify({"err": str(err)})

        if request.method == 'GET':
            try:
                client = create_client(request)

                database = client.DATABASE_NAME

                deposit_id = get_value(request=request, scope='config', field='deposit_id')
                collection = get_value(request=request, scope='config', field='collection')

                posts = database.posts
                
                temp_obj_path = str(deposit_id)
                obj = client.find_one(deposit_id)

                return send_file(temp_obj_path, mimetype="application/octet-stream")
                return jsonify(client.find_one({"deposit_id":deposit_id})
            
            except Exception as err:
                return jsonify({"err": str(err)})

        if request.method == 'DELETE':
            try:
                client = create_client(request)

                database = client.DATABASE_NAME

                deposit_id = get_value(request=request, scope='data', field='deposit_id')
                collection = get_value(request=request, scope='config', field='collection')
                posts = collection.posts
                del_obj = posts.delete_one({"deposit_id": deposit_id})

                if del_obj:
                    return jsonify({"del_obj": deposit_id})
                else:
                    return jsonify({"err":"Document not deleted."})

            except Exception as err:
                return jsonify({"err": str(err)})

    if __name__ == '__main__':
        app.run(debug=True)