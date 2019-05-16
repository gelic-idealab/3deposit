import os
import json
from json import JSONDecodeError
from flask import Flask, request, jsonify, send_file
from minio import Minio
from minio.error import ResponseError, BucketAlreadyExists, NoSuchBucket, NoSuchKey

# ACCESS KEY AKIAIOSFODNN7GRAINGER
# SECRET KEY wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY

# if sys.argv(2):
#     SERVER_ENDPOINT = 'minio-server:9000'
# else:
#     SERVER_ENDPOINT = 'localhost:9000'

SERVER_ENDPOINT = 'minio-server:9000'

BUCKET_NAME = '3deposit'

def minio_keys(request_auth):
    if not request_auth:
        return False
    
    auth = request_auth.form.get('auth')
    
    if auth:
        auth = json.loads(request_auth.form.get('auth'))
        auth_packed = {"access_key":auth.get('access_key'),"secret_key":auth.get('secret_key')}
        return auth_packed
    else:
        return False

def create_app():
    app = Flask(__name__)

    @app.route('/minio', methods=['GET', 'POST','DELETE'])
    def minio():
        if request.method == 'GET':
            # get keys from request args

            if minio_keys(request):
                auth = minio_keys(request)
            else:
                return jsonify({"err": "No authentication keys provided"})

            try:
                # Initialize minioClient with an endpoint and keys.
                minioClient = Minio(SERVER_ENDPOINT,
                                    access_key=auth.get("access_key"),
                                    secret_key=auth.get("secret_key"),
                                    secure=False)

                deposit_id = False
                # get data from request payload
                try:
                    data = request.form.get('data')
                    try:
                        data = json.loads(request.form.get('data'))
                        deposit_id = data.get('deposit_id')
                        metadata = data.get('metadata')
                    except JSONDecodeError as err:
                        return jsonify({"err":"Incorrect formatting of data"})
                except TypeError as err:
                    return jsonify({"err": "No data provided"})

                if not deposit_id:
                    return jsonify({"err": "No deposit ID provided"})
                # get objects from bucket

                # construct response object from objects iterable

                # try:
                #     data = minioClient.get_object(BUCKET_NAME, deposit_id)
                # except NoSuchKey as err:
                #     print(err)

                temp_obj_path = str(deposit_id)

                try:
                    obj = minioClient.get_object(BUCKET_NAME, deposit_id)
                    try:
                        with open(temp_obj_path, 'wb') as file_data:
                            for d in obj.stream(32*1024):
                                file_data.write(d)
                    except Exception as err:
                        return jsonify({"err":str(err)})
                except NoSuchKey as err:
                    return jsonify({"err":str(err)})

                # check whether object exists in the bucket

                #objects_list = []
                #for i,obj in enumerate(objects):
                if obj:
                    if metadata == "1":
                        meta_obj = minioClient.fget_object(BUCKET_NAME,object_name=deposit_id,file_path=deposit_id)
                        ret_object =   {"metadata": str(meta_obj.metadata), 
                                        "deposit_id": str(meta_obj.object_name), 
                                        "modified": str(meta_obj.last_modified),
                                        "etag": str(meta_obj.etag), 
                                        "size": str(meta_obj.size), 
                                        "content_type": str(meta_obj.content_type)}
                        return jsonify(ret_object)
                    else:
                        return send_file(temp_obj_path, mimetype="application/octet-stream")

                    # if i == len(objects) - 1:
                    #     return jsonify({ "err": "Object does not exist." })
                    # objects_list.append({ "bucket": str(obj.bucket_name), 
                    #                       "deposit_id": str(obj.object_name), 
                    #                       "modified": str(obj.last_modified),
                    #                       "etag": str(obj.etag), 
                    #                       "size": str(obj.size), 
                    #                       "content_type": str(obj.content_type) })

                #return jsonify({ "objects": objects_list })

            except ResponseError as err:
                return jsonify({"err": err})


        elif request.method == 'POST':
            # get data from request payload
            data = json.loads(request.form.get('data'))
            
            # extract authentication details
            auth = minio_keys(request)

            # extract deposit_id value
            deposit_id = data.get('deposit_id')

            # extract file & temp save to disk
            file = request.files['file']
            file.save(deposit_id)

            # Initialize minioClient with an endpoint and keys.
            minioClient = Minio(SERVER_ENDPOINT,
                                access_key=auth.get("access_key"),
                                secret_key=auth.get("secret_key"),
                                secure=False)   

            # print(minioClient.bucket_exists(BUCKET_NAME))
            if not minioClient.bucket_exists(BUCKET_NAME):
                try:
                    minioClient.make_bucket(BUCKET_NAME)
                except Exception as err:
                    return jsonify({"err": err})                    

            metadata={}

            metadata['BUCKET_NAME'] = BUCKET_NAME

            try:
                r = minioClient.fput_object(BUCKET_NAME, object_name=deposit_id, file_path=deposit_id,metadata=metadata)
                # cleanup temp file
                os.remove(deposit_id)
                return jsonify({"etag": r, "deposit_id": deposit_id,"metadata":metadata})

            except ResponseError as err:
                return jsonify({"err": err})

        elif request.method == 'DELETE':
            # extract authentication details
            auth = minio_keys(request)

            # get data from request payload
            data = json.loads(request.form.get('data'))

            # extract object specific deposit_id
            deposit_id = data.get('deposit_id')

            minioClient = Minio(SERVER_ENDPOINT,
                                access_key=auth.get("access_key"),
                                secret_key=auth.get("secret_key"),
                                secure=False)

            try:
                rem_object = minioClient.remove_object(BUCKET_NAME,deposit_id)
            except ResponseError as err:
                return jsonify({"error":err})

            return jsonify({"deposit_id": deposit_id})

        else:
            return jsonify({"err":"Unsupported method"})
    
#**************************************************************************************************************************************************************************************************************************************
    
    @app.route('/bucket', methods=['GET'])
    def bucket():
        if request.method == 'GET':
            # get keys from request args

            if minio_keys(request):
                auth = minio_keys(request)
            else:
                return jsonify({"err": "No authentication keys provided"})


            try:
                # Initialize minioClient with an endpoint and keys.
                minioClient = Minio(SERVER_ENDPOINT,
                                    access_key=auth.get("access_key"),
                                    secret_key=auth.get("secret_key"),
                                    secure=False)

                deposit_id_list = []
                # get data from request payload
                if request.form.get('data'):
                    if json.loads(request.form.get('data')):
                        data = json.loads(request.form.get('data'))
                        deposit_id_list = data.get('deposit_id_list')
                        if not deposit_id_list:
                            return jsonify({"err": "No deposit ID provided"})                

                # get objects from bucket
                if minioClient.bucket_exists(BUCKET_NAME):
                    objects = minioClient.list_objects(BUCKET_NAME, recursive=True)
                else:
                    return jsonify({ "err": "Bucket does not exist." })

                obj_names = []
                missing_ids = []
                test_ids = []

                objects_list = []

                if deposit_id_list:
                    for obj in objects:
                        if obj.object_name not in deposit_id_list:
                            continue
                        ret_object = {"metadata": str(obj.metadata), 
                                      "deposit_id": str(obj.object_name), 
                                      "modified": str(obj.last_modified),
                                      "etag": str(obj.etag), 
                                      "size": str(obj.size), 
                                      "content_type": str(obj.content_type)}
                        objects_list.append(ret_object)

                    for i,d in enumerate(deposit_id_list):
                        if d not in obj_names:
                            missing_ids.append(d)

                else:
                    for obj in objects:
                        ret_object = {"metadata": str(obj.metadata), 
                                      "deposit_id": str(obj.object_name), 
                                      "modified": str(obj.last_modified),
                                      "etag": str(obj.etag), 
                                      "size": str(obj.size), 
                                      "content_type": str(obj.content_type)}
                        objects_list.append(ret_object)
                    #obj_names.append(str(obj.object_name))



                return jsonify({"objects": objects_list,"missing deposit ids":missing_ids})

            except ResponseError as err:
                return jsonify({"err": err})

    return app