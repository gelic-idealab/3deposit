import os
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

app = Flask(__name__)

@app.route('/minio', methods=['POST'])
def box():
    if request.method == 'POST':
        response = {}
        post_data = json.loads(request.form.get('data'))
        metadata = post_data.get('metadata')
        deposit_id = metadata['deposit_id']
        file = request.files['file']
        file.save(file_path)

        OBJECT_PATH = deposit_id

        # Initialize minioClient with an endpoint and keys.
        minioClient = Minio('localhost:9000',
                            access_key='AKIAIOSFODNN7GRAINGER',
                            secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY',
                            secure=False)

        try:
            r = minioClient.fput_object('3deposit', OBJECT_PATH, OBJECT_PATH)
            return jsonify({"etag": r})
        except ResponseError as err:
            return jsonify({"error": err})


if __name__ == '__main__':
    app.run()
