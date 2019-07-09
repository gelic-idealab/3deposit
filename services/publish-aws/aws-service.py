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

from keys import ACCESS_KEY, SECRET_KEY

app = Flask(__name__) 

@app.route('/', methods=['POST', 'GET', 'DELETE'])
def index():
    if request.method == 'POST':
        try:
            config = request.form.get('config')
            data = request.form.get('data')
            # use deposit id as directory name
            TMP_DIR = data.get('deposit_id')
            # get deposit file and save to temporary location
            deposit_file = request.files['file']
            deposit_file.save('tmp.zip')
            deposit_file.close()

            # Connect to S3
            c = boto.connect_s3(ACCESS_KEY, SECRET_KEY)
            b = c.get_bucket(BUCKET_NAME)

            # unzip into directory and remove tmp file
            with zipfile.ZipFile('tmp.zip','r') as zip_ref:
                zip_ref.extractall(TMP_DIR)
            os.remove('tmp.zip')

            file_paths = []
            def get_file_paths(tmp_dir):
                for dir_, _, files in os.walk(tmp_dir):
                    for file_name in files:
                        rel_dir = os.path.relpath(dir_, tmp_dir)
                        rel_file = os.path.join(TMP_DIR, rel_dir, file_name)
                        file_paths.append(rel_file)
                return file_paths

            fps = get_file_paths(TMP_DIR)
            print(fps)


            # Get file info
            try: 
                for f in fps:
                    source_path = f
                    source_size = os.stat(source_path).st_size
                    print(source_path)

                    # Create a multipart upload request
                    content_type = str(mimetypes.guess_type(source_path)[0])
                    print(content_type)
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
            finally:
                if os.path.exists(TMP_DIR):
                    shutil.rmtree(TMP_DIR)
            return jsonify ({ 'uuid': TMP_DIR })

if __name__ == '__main__':
    app.run()