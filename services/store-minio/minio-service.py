import os
import json
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import ResponseError, BucketAlreadyExists, NoSuchBucket


# ACCESS KEY AKIAIOSFODNN7GRAINGER
# SECRET KEY wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY

SERVER_ENDPOINT = 'minio-server:9000'
BUCKET_NAME = '3deposit'

def minio_keys(request_auth):
    auth = json.loads(request_auth.form.get('auth'))
    access_key = auth.get('access_key')
    secret_key = auth.get('secret_key')

    auth_packed = {"access_key":access_key,"secret_key":secret_key}

    return auth_packed

def create_app():
    app = Flask(__name__)

    @app.route('/minio', methods=['GET', 'POST','DELETE'])
    def minio():
        if request.method == 'GET':
            # get keys from request args
            auth = minio_keys(request)
            
            access_key = auth.get("access_key")
            secret_key = auth.get("secret_key")

            try:
                # Initialize minioClient with an endpoint and keys.
                minioClient = Minio(SERVER_ENDPOINT,
                                    access_key=access_key,
                                    secret_key=secret_key,
                                    secure=False)

                # get objects from bucket
                if minioClient.bucket_exists(BUCKET_NAME):
                    objects = minioClient.list_objects(BUCKET_NAME, recursive=True)
                else:
                    return jsonify({ "err": "Bucket does not exist." })

                # construct response object from objects iterable
                objects_list = []
                for obj in objects:
                    objects_list.append({ "bucket": str(obj.bucket_name), 
                                          "deposit_id": str(obj.object_name), 
                                          "modified": str(obj.last_modified),
                                          "etag": str(obj.etag), 
                                          "size": str(obj.size), 
                                          "content_type": str(obj.content_type) })

                return jsonify({ "objects": objects_list })

            except ResponseError as err:
                return jsonify({"err": err})


        elif request.method == 'POST':
            # get data from request payload
            data = json.loads(request.form.get('data'))
            
            # extract authentication details
            auth = minio_keys(request)
            
            access_key = auth.get("access_key")
            secret_key = auth.get("secret_key")

            # extract deposit_id value
            deposit_id = data.get('deposit_id')

            # extract file & temp save to disk
            file = request.files['file']
            file.save(deposit_id)

            # Initialize minioClient with an endpoint and keys.
            minioClient = Minio(SERVER_ENDPOINT,
                                access_key=access_key,
                                secret_key=secret_key,
                                secure=False)   

            # print(minioClient.bucket_exists(BUCKET_NAME))
            if not minioClient.bucket_exists(BUCKET_NAME):
                try:
                    minioClient.make_bucket(BUCKET_NAME)
                except Exception as err:
                    return jsonify({"error": err})                    

            try:
                r = minioClient.fput_object(BUCKET_NAME, deposit_id, deposit_id)
                # cleanup temp file
                os.remove(deposit_id)
                return jsonify({"etag": r, "deposit_id": deposit_id})

            except ResponseError as err:
                return jsonify({"error": err})

        elif request.method == 'DELETE':
            # extract authentication details
            auth = minio_keys(request)
            
            access_key = auth.get("access_key")
            secret_key = auth.get("secret_key")

            # get data from request payload
            data = json.loads(request.form.get('data'))

            # extract object specific deposit_id
            deposit_id = data.get('deposit_id')

            minioClient = Minio(SERVER_ENDPOINT,
                                access_key=access_key,
                                secret_key=secret_key,
                                secure=False)

            try:
                rem_object = minioClient.remove_object(BUCKET_NAME,deposit_id)
            except ResponseError as err:
                return jsonify({"error":err})

            return jsonify({"deposit_id": deposit_id})

        else:
            return jsonify({"err":"Unsupported method"})
    
    return app
