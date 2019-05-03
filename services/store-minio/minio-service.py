import os
import json
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import ResponseError, BucketAlreadyExists


# ACCESS KEY AKIAIOSFODNN7GRAINGER
# SECRET KEY wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY

SERVER_ENDPOINT = 'minio-server:9000'
BUCKET_NAME = '3deposit'


def create_app():
    app = Flask(__name__)

    @app.route('/minio', methods=['GET', 'POST'])
    def minio():
        if request.method == 'GET':
            # get keys from request args
            access_key = request.args.get('access_key')
            secret_key = request.args.get('secret_key')

            try:
                # Initialize minioClient with an endpoint and keys.
                minioClient = Minio(SERVER_ENDPOINT,
                                    access_key=access_key,
                                    secret_key=secret_key,
                                    secure=False)

                # get objects from bucket
                objects = minioClient.list_objects(BUCKET_NAME, recursive=True)

                # construct response object from objects iterable
                objects_list = []
                for obj in objects:
                    objects_list.append({"bucket": str(obj.bucket_name), "deposit_id": str(obj.object_name), "modified": str(obj.last_modified),
                        "etag": str(obj.etag), "size": str(obj.size), "content_type": str(obj.content_type)})       
                return jsonify({"objects": objects_list})

            except ResponseError as err:
                return jsonify({"err": err})


        else:
            # get data from request payload
            data = json.loads(request.form.get('data'))

            # extract metadata object & needed values
            metadata = data.get('metadata')
            deposit_id = metadata['deposit_id']

            # extract authentication credentials
            auth = data.get('auth')
            access_key = auth.get('access_key')
            secret_key = auth.get('secret_key')

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
    
    return app
