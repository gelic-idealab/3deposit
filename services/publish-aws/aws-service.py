import os
import math
import json
from flask import Flask, request, jsonify
import logging
import boto
from boto.s3.connection import S3Connection
from filechunkio import FileChunkIO
import zipfile
import mimetypes
import shutil
from uuid import uuid4

from unpack.unpack import get_value
app = Flask(__name__) 

@app.route('/', methods=['POST', 'GET', 'DELETE'])
def index():
    try:
        # get keys from request object
        access_key = get_value(request, 'config', 'access_key')
        secret_key = get_value(request, 'config', 'secret_key')

        # get AWS S3 bucket name being used for static hosting
        bucket_name = get_value(request, 'config', 'bucket_name')
        logging.debug(bucket_name)

        # Connect to S3
        c = boto.connect_s3(access_key, secret_key)
        b = c.get_bucket(bucket_name)

        if request.method == 'POST':

            # get deposit it and use as temporary directory name
            deposit_id = get_value(request, 'data', 'deposit_id')
            logging.debug(deposit_id)
            
            # get deposit file and save to temporary location
            deposit_file = request.files['file']
            deposit_file.save('tmp.zip')
            deposit_file.close()

            # unzip into directory and remove tmp file
            with zipfile.ZipFile('tmp.zip','r') as zip_ref:
                zip_ref.extractall(deposit_id)
            os.remove('tmp.zip')

            file_paths = []

            def get_file_paths(tmp_dir):
                for dir_, _, files in os.walk(tmp_dir):
                    for file_name in files:
                        rel_dir = os.path.relpath(dir_, tmp_dir)
                        rel_file = os.path.join(tmp_dir, rel_dir, file_name)
                        file_paths.append(rel_file)
                return file_paths

            fps = get_file_paths(deposit_id)
            print(fps)


            # Get file info
            for f in fps:
                source_path = f
                source_size = os.stat(source_path).st_size
                print(source_path)

                # Create a multipart upload request
                content_type = str(mimetypes.guess_type(source_path)[0])
                mp = b.initiate_multipart_upload(source_path, policy='public-read', headers = {'Content-Type': content_type})

                # Use a chunk size of 50 MiB (feel free to change this)
                chunk_size = 52428800
                chunk_count = int(math.ceil(source_size / float(chunk_size)))

                # Send the file parts, using FileChunkIO to create a file-like object
                # that points to a certain byte range within the original file. We
                # set bytes to never exceed the original file size.
                for i in range(chunk_count):
                    offset = chunk_size * i
                    bytes = min(chunk_size, source_size - offset)
                    with FileChunkIO(source_path, 'r', offset=offset, bytes=bytes) as fp:
                        mp.upload_part_from_file(fp, part_num=i + 1)

                    # Finish the upload
                    mp.complete_upload()

            # walk until first html is found
            for f in fps:
                source_path = f
                if source_path.endswith('.html'):
                    index_path = source_path
                    break

            if os.path.exists(deposit_id):
                shutil.rmtree(deposit_id)

            # return deposit id as resource id and build object url from bucket name
            # https://<bucket_name>.s3.amazonaws.com/<deposit_id>
            return jsonify({ 
                'resource_id': deposit_id,
                'location': f'https://{bucket_name}.s3.amazonaws.com/{index_path}'
                })

        elif request.method == 'GET':
            resource_id = get_value(request, 'data', 'resource_id')
            obj_list = []
            attr_list = ['metadata', 'content_type', 'etag', 'last_modified', 'md5', 'storage_class', 'size']
            length = 0

            for obj in b.list(prefix=resource_id):
                obj_metadata = {}
                obj_metadata.update({'s3_key_name': obj.name})
                for attr in attr_list:
                    obj_metadata.update({attr: getattr(obj, attr)})
                obj_list.append(obj_metadata)
                length += 1

            return jsonify({'metadata': obj_list, 'files': length})

    except Exception as err:
        return jsonify({'err': str(err)})


if __name__ == '__main__':
    app.run()