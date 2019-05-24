import os
import json
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import ResponseError, BucketAlreadyExists, NoSuchBucket

class Keys:
	def minio_keys():
		auth = json.loads(request.form.get('auth'))
            
        access_key = auth.get('access_key')
        secret_key = auth.get('secret_key')

        return jsonify({"access_key":access_key,"secret_key":secret_key})