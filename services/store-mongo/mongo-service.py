import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

# https://api.mongodb.com/python/current/tutorial.html

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

    
    DATABASE_NAME = 'deposits'
    COLLECTION_NAME = 'metadata'
    username = 'root'
    password = 'example'
    
    database = client[DATABASE_NAME]
    collection = database[COLLECTION_NAME]

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
    if remote:
        provider = get_value(request=request, scope='config', field='provider').lower()
        if provider == 'aws':
            server_endpoint = 's3.amazonaws.com'
            region = get_value(request=request, scope='config', field='region').lower()

        elif provider == 'azure':
            True
        elif provider == 'google cloud':
            True
    else:
        server_endpoint = 'minio-server:9000'

    client = MongoClient(
        'mongodb://{username}:{password}@localhost:27017/'.format(
        username=username,
        password=password
        )
    )

    if server_endpoint == 'err':
        return {"err":"Please enter a valid provider."}

    #except Exception as err:
    #   return err

    return minioClient
    
def create_app()
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
                #config = json.loads(request.form.get('config'))
                # db_name = client.MongoTest2
                # data = json.loads(request.form.get('data'))

                db_name = get_value(request=request, scope='config', field='db_name')
                deposit_id = get_value(request=request, scope='data', field='deposit_id')

                posts = db_name.posts
                post_id = posts.insert_one(data).inserted_id
                return jsonify({"post_id": str(post_id)})

            except Exception as err:
                return jsonify({"err": str(err)})

        if request.method == 'GET':
            try:
                # config = json.loads(request.form.get('config'))
                # db_name = config.get('db_name')
                #db_name = client.MongoTest2
                #data = json.loads(request.form.get('data'))
                deposit_id = get_value(request=request, scope='config', field='deposit_id')
                db_name = get_value(request=request, scope='config', field='db_name')

                posts = db_name.posts

                temp_obj_path = str(deposit_id)
                    obj = minioClient.get_object(bucket_name, deposit_id)

                with open(temp_obj_path, 'wb') as file_data:
                    for d in obj.stream(32*1024):
                        file_data.write(d)

                return send_file(temp_obj_path, mimetype="application/octet-stream")

                metadata_obj_iter = posts.find({"deposit_id":deposit_id})
                metadata_obj_iter_list = [i for i in metadata_obj_iter]
                num_metadata_objs = len(metadata_obj_iter_list)

                if num_metadata_objs > 1:
                    list_of_metadata_objs = [
                        str('{"metadata_obj": ' + str(obj) + '}')
                        for obj in metadata_obj_iter_list ]

                    # Assign the most recently added 3D metadata object with the
                    # particular deposit_id of interest to "most_recent_metadata_obj"
                    most_recent_metadata_obj = metadata_obj_iter_list[-1]

                    return jsonify({
                        "err":"You have more than one 3D metadata object with the \
                        same deposit_id in your database! We are returning a list \
                        of these objects back to you; however, you should consider \
                        consolidating them...",
                        "list_of_metadata_objs": list_of_metadata_objs,
                        "most_recent_metadata_obj": str(most_recent_metadata_obj)
                        })
                else:
                    metadata_obj = metadata_obj_iter_list[0]
                    # metadata_obj = posts.find_one({"deposit_id":deposit_id})
                    return jsonify({"metadata_obj": str(metadata_obj)})

            except Exception as err:
                return jsonify({"err": str(err)})

        if request.method == 'DELETE':
            try:
                # config = json.loads(request.form.get('config'))
                # db_name = config.get('db_name')
                # db_name = client.MongoTest2
                # data = json.loads(request.form.get('data'))
                deposit_id = get_value(request=request, scope='data', field='deposit_id')
                db_name = get_value(request=request, scope='config', field='db_name')
                posts = db_name.posts
                del_obj = posts.delete_one({"deposit_id": deposit_id})

                # NOTE: If there are >1 documents with the same deposit_id
                # (for instance, if one of them was inserted twice,
                # creating a duplicate entry), then just one of them
                # is deleted (in the same order as when each was added
                # --i.e., the first one that was added will be the first
                # one that's deleted.)

                return jsonify({"del_obj": str(del_obj)})
            except Exception as err:
                return jsonify({"err": str(err)})

    if __name__ == '__main__':
        app.run(debug=True)