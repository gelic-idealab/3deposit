# import os
# import math
# import json
# import requests
# from flask import Flask, request, jsonify
# import logging
# import boto
# from filechunkio import FileChunkIO

# from keys import ACCESS_KEY, SECRET_KEY

# app = Flask(__name__) 

# @app.route('/', methods=['POST', 'GET', 'DELETE'])
# def index():
#     if request.method == 'POST':
#         conn = S3Connection(ACCESS_KEY, SECRET_KEY)

#         # Connect to S3
#         c = boto.connect_s3()
#         b = c.get_bucket('3deposit')

#         # Get file info
#         source_path = './webvr'
#         source_size = os.stat(source_path).st_size

#         # Create a multipart upload request
#         mp = b.initiate_multipart_upload(os.path.basename(source_path))

#         # Use a chunk size of 50 MiB (feel free to change this)
#         chunk_size = 52428800
#         chunk_count = int(math.ceil(source_size / float(chunk_size)))

#         # Send the file parts, using FileChunkIO to create a file-like object
#         # that points to a certain byte range within the original file. We
#         # set bytes to never exceed the original file size.
#         for i in range(chunk_count):
#             offset = chunk_size * i
#             bytes = min(chunk_size, source_size - offset)
#             with FileChunkIO(source_path, 'r', offset=offset,
#                     bytes=bytes) as fp:
#                 mp.upload_part_from_file(fp, part_num=i + 1)

#         # Finish the upload
#         mp.complete_upload()

import os
import math
import json
from flask import Flask, request, jsonify
import logging
import boto
from filechunkio import FileChunkIO

from keys import ACCESS_KEY, SECRET_KEY


# conn = S3Connection(ACCESS_KEY, SECRET_KEY)

# Connect to S3
c = boto.connect_s3(ACCESS_KEY, SECRET_KEY)
b = c.get_bucket('new-3deposit')

# Get file info
source_path = './webvr.zip'
source_size = os.stat(source_path).st_size

# Create a multipart upload request
mp = b.initiate_multipart_upload(os.path.basename(source_path))

# Use a chunk size of 50 MiB (feel free to change this)
chunk_size = 52428800
chunk_count = int(math.ceil(source_size / float(chunk_size)))

# Send the file parts, using FileChunkIO to create a file-like object
# that points to a certain byte range within the original file. We
# set bytes to never exceed the original file size.
for i in range(chunk_count):
    offset = chunk_size * i
    bytes = min(chunk_size, source_size - offset)
    with FileChunkIO(source_path, 'r', offset=offset,
            bytes=bytes) as fp:
        mp.upload_part_from_file(fp, part_num=i + 1)

# Finish the upload
mp.complete_upload()