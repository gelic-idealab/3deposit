import os
import json
from flask import Flask, request, jsonify, send_file
from minio import Minio
from minio.error import ResponseError, BucketAlreadyExists, NoSuchBucket, NoSuchKey

# ACCESS KEY AKIAIOSFODNN7GRAINGER
# SECRET KEY wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY

SERVER_ENDPOINT = 'minio-server:9000'
BUCKET_NAME = '3deposit'

def minio_keys(request_auth):
    auth = json.loads(request_auth.form.get('auth'))
    auth_packed = {"access_key":auth.get('access_key'),"secret_key":auth.get('secret_key')}

    return auth_packed

def create_app():
    app = Flask(__name__)

    @app.route('/minio', methods=['GET', 'POST','DELETE'])
    def minio():
        if request.method == 'GET':
            # get keys from request args

            if minio_keys(request):
                auth = minio_keys(request)
            else:
                return jsonify({"err": "No auth keys provided"})

            try:
                # Initialize minioClient with an endpoint and keys.
                minioClient = Minio(SERVER_ENDPOINT,
                                    access_key=auth.get("access_key"),
                                    secret_key=auth.get("secret_key"),
                                    secure=False)

                # get data from request payload
                if json.loads(request.form.get('data')):
                    data = json.loads(request.form.get('data'))
                    deposit_id = data.get('deposit_id')
                    metadata = data.get('metadata')
                else:
                    return jsonify({"err": "No deposit ID provided"})                

                # get objects from bucket

                # construct response object from objects iterable

                # try:
                #     data = minioClient.get_object(BUCKET_NAME, deposit_id)
                # except NoSuchKey as err:
                #     print(err)

                try:
                    obj = minioClient.get_object(BUCKET_NAME, deposit_id)
                    try:
                        with open(str(deposit_id), 'wb') as file_data:
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
                    # meta_obj = minioClient.stat_object(BUCKET_NAME,deposit_id)
                    # ret_object =   {"metadata": str(meta_obj.metadata), 
                    #                 "deposit_id": str(meta_obj.object_name), 
                    #                 "modified": str(meta_obj.last_modified),
                    #                 "etag": str(meta_obj.etag), 
                    #                 "size": str(meta_obj.size), 
                    #                 "content_type": str(meta_obj.content_type)}
                    # return jsonify(ret_object)
                    return send_file(str(deposit_id), mimetype="application/octet-stream")

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

            try:
                r = minioClient.fput_object(BUCKET_NAME, deposit_id, content_type='application/octet-stream')
                # cleanup temp file
                os.remove(deposit_id)
                return jsonify({"etag": r, "deposit_id": deposit_id})

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
    @app.route('/bucket', methods=['GET', 'POST'])
    def bucket():
        if request.method == 'GET':
            # get keys from request args

            if minio_keys(request):
                auth = minio_keys(request)
            else:
                return jsonify({"err": "No auth keys provided"})

            try:
                # Initialize minioClient with an endpoint and keys.
                minioClient = Minio(SERVER_ENDPOINT,
                                    access_key=auth.get("access_key"),
                                    secret_key=auth.get("secret_key"),
                                    secure=False)

                # get data from request payload
                if json.loads(request.form.get('data')):
                    data = json.loads(request.form.get('data'))
                    deposit_id_list = data.get('deposit_id_list')
                else:
                    return jsonify({"err": "No deposit ID provided"})                

                # get objects from bucket
                if minioClient.bucket_exists(BUCKET_NAME):
                    objects = minioClient.list_objects(BUCKET_NAME, recursive=True)
                else:
                    return jsonify({ "err": "Bucket does not exist." })


                # try:
                #     obj = minioClient.get_object(BUCKET_NAME, deposit_id)
                #     with open(str(deposit_id), 'wb') as file_data:
                #         for d in obj.stream(32*1024):
                #             file_data.write(d)
                # except NoSuchKey as err:
                #     return jsonify({"err":str(err)})

                obj_names = []
                missing_ids = []
                test_ids = []

                #return jsonify({"test_ids":test_ids,"missing_ids":missing_ids})

                # for i,obj in enumerate(objects):
                #     if obj.object_name not in deposit_id_list:
                #         objects.remove(i)

                objects_list = []
                for obj in objects:
                    # try:
                    if obj.object_name not in deposit_id_list:
                        continue
                    ret_object = {"metadata": str(obj.metadata), 
                                  "deposit_id": str(obj.object_name), 
                                  "modified": str(obj.last_modified),
                                  "etag": str(obj.etag), 
                                  "size": str(obj.size), 
                                  "content_type": str(obj.content_type)}
                    objects_list.append(ret_object)

                    obj_names.append(str(obj.object_name))

                for i,d in enumerate(deposit_id_list):
                    if d not in obj_names:
                        missing_ids.append(d)

                return jsonify({"objects": objects_list,"missing deposit ids":missing_ids})
                #return str(objects)
                # construct response object from objects iterable

                # try:
                #     data = minioClient.get_object(BUCKET_NAME, deposit_id)
                # except NoSuchKey as err:
                #     print(err)

                # check whether object exists in the bucket

                #objects_list = []
                #for i,obj in enumerate(objects):
                #if obj:
                    # meta_obj = minioClient.stat_object(BUCKET_NAME,deposit_id)
                    # ret_object =   {"metadata": str(meta_obj.metadata), 
                    #                 "deposit_id": str(meta_obj.object_name), 
                    #                 "modified": str(meta_obj.last_modified),
                    #                 "etag": str(meta_obj.etag), 
                    #                 "size": str(meta_obj.size), 
                    #                 "content_type": str(meta_obj.content_type)}
                    # return jsonify(ret_object)
                    #return send_file(str(deposit_id), mimetype="application/octet-stream")

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

            try:
                r = minioClient.fput_object(BUCKET_NAME, deposit_id, deposit_id)
                # cleanup temp file
                os.remove(deposit_id)
                return jsonify({"etag": r, "deposit_id": deposit_id})

            except ResponseError as err:
                return jsonify({"err": err})        

    return app
