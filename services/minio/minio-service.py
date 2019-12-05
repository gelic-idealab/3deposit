import os
import json
import logging
from json import JSONDecodeError
from flask import Flask, request, jsonify, send_file, make_response
from minio import Minio
from minio.error import ResponseError, BucketAlreadyExists, NoSuchBucket, NoSuchKey, AccessDenied
from minio.error import SignatureDoesNotMatch, InvalidBucketError, InvalidAccessKeyId, SignatureDoesNotMatch, BucketAlreadyOwnedByYou
from werkzeug.exceptions import BadRequestKeyError

from unpack.unpack import get_value


def minio_keys(request):
    if not request:
        return False
    try:
        config = json.loads(request.form.get('config'))
        auth = config.get('auth')
        auth_packed = {"access_key": auth.get('access_key'), "secret_key": auth.get('secret_key')}
        return auth_packed
    except JSONDecodeError as err:
        return {"err": "Invalid formatting of data.",
                "log": str(err)}
    except (InvalidAccessKeyId, SignatureDoesNotMatch, AccessDenied) as err:
        return {"err": "Invalid Authentication.",
                "log": str(err)}
    except AttributeError as err:
        return {"err": "Please provide auth keys.",
                "log": str(err)}
    except Exception as err:
        return {"err": "General Exception",
                "log": str(err),
                "req_json": request.json}


def create_client(request):
    if not request:
        return False
    logging.debug(msg='creating minio client')
    # try:
    minioClient = ''
    config = json.loads(request.form.get('config'))
    auth = config.get('auth')
    remote = config.get('remote')
    region = None
    server_endpoint = 'err'

    if minio_keys(request):
        auth = minio_keys(request)
        if "err" in auth:
            return auth
    else:
        return {"err": "No authentication keys provided"}
    if remote:
        provider = config.get('provider').lower()
        if provider == 'aws':
            server_endpoint = 's3.amazonaws.com'
            region = config.get('region')

        elif provider == 'azure':
            True
        elif provider == 'google cloud':
            True
    else:
        server_endpoint = 'minio-server:9000'

    minioClient = Minio(endpoint=server_endpoint,
                        access_key=auth.get("access_key"),
                        secret_key=auth.get("secret_key"),
                        region=region,
                        secure=False)

    if server_endpoint == 'err':
        return {"err": "Please enter a valid provider."}

    return minioClient


def create_app():
    app = Flask(__name__)

    # logging boilerplate
    service_name = str(os.path.basename(__file__))
    logfile = 'service.log'
    logging.basicConfig(level=logging.DEBUG, filename=logfile)
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.info(f'Starting {service_name}...')

    @app.route('/log', methods=['GET'])
    def log_handler():
        try:
            with open(logfile, 'r') as f:
                l = f.read()
                ll = l.split('\n')
            return jsonify({'log': ll})
        except Exception as err:
            logging.error(f'/log error: {str(err)}')
            return jsonify({'err': str(err)})


    # AT THIS ENDPOINT, EACH ACTION IS SPECIFIC TO AN OBJECT AT ITS CORE

    @app.route('/object', methods=['GET', 'POST','DELETE'])
    def object():

        # Extract an object from a specified bucket

        if request.method == 'GET':
            # get keys from request args

            try:
                # select endpoint
                minioClient = create_client(request)

                if type(minioClient) == dict and 'err' in minioClient:
                    return jsonify(minioClient)

                config = json.loads(request.form.get('config'))
                deposit_id = config.get('deposit_id')
                bucket_name = config.get('bucket_name')

                temp_obj_path = str(deposit_id)
                obj = minioClient.get_object(bucket_name, deposit_id)

                with open(temp_obj_path, 'wb') as file_data:
                    for d in obj.stream(32*1024):
                        file_data.write(d)

                res = make_response(send_file(temp_obj_path, mimetype="application/octet-stream"))
                return res

            except NoSuchKey as err:  # Handle deposit_id related error
                return jsonify({"err": "Please provide a valid deposit_id",
                                "log": str(err)})
            except (InvalidBucketError, NoSuchBucket) as err:  # Handle bucket_name related errors
                return jsonify({"err": "Please provide valid bucket_name",
                                "log": str(err)})
            except (AccessDenied, InvalidAccessKeyId, SignatureDoesNotMatch) as err:  # Handle authentication related errors
                return jsonify({"err": "Invalid Authentication.",
                                "log": str(err)})
            except JSONDecodeError as err:  # Handle formatting related errors
                return jsonify({"err": "Incorrect formatting of data",
                                "log": str(err)})
            except ResponseError as err:
                return jsonify({"err": str(err),
                                "log": str(err)})
            except TypeError as err:  # Handle bucket_name and/or deposit_id related errors
                return jsonify({"err": "Please provide valid bucket_name and deposit_id",
                                "log": str(err)})

        # Puts one object i.e. a file in the specified bucket only.

        elif request.method == 'POST':
            logging.debug(msg='POST request received')
            # get data from request payload
            try:
                config = json.loads(request.form.get('config'))
                data = json.loads(request.form.get('data'))

                minioClient = create_client(request)
                # print(type(minioClient))

                if type(minioClient) == dict and 'err' in minioClient:
                    return jsonify(minioClient) 

                # extract deposit_id value
                if data.get('deposit_id'):
                    deposit_id = data.get('deposit_id')
                else:
                    return jsonify({"err": "Please provide a deposit_id",
                                    "log": str(err)})
                
                logging.debug(msg='Processing deposit: {}'.format(deposit_id))

                # extract file & temp save to disk
                file = request.files['file']
                file.save(deposit_id)

                # extract bucket_name value
                bucket_name = config.get('bucket_name')
                if not minioClient.bucket_exists(bucket_name):
                    minioClient.make_bucket(bucket_name)

                metadata = {}
                metadata['BUCKET_NAME'] = bucket_name

                r = minioClient.fput_object(bucket_name, object_name=deposit_id, file_path=deposit_id, metadata=metadata)
                # cleanup temp file
                logging.debug(msg='fput_object op returned: {}'.format(str(r)))

                return jsonify({"etag": r, "deposit_id": deposit_id, "metadata": metadata})

            except (NoSuchBucket, InvalidBucketError) as err:  # Handle bucket_name related errors
                return jsonify({"err": "This bucket does not exist. Please create this bucket at the bucket scoped endpoint.",
                                "log": str(err)})
            except TypeError as err:  # Handle bucket_name related errors
                return jsonify({"err": "Please enter a bucket_name",
                                "log": str(err)})
            except (InvalidAccessKeyId, AccessDenied, SignatureDoesNotMatch) as err:  # Handle authentication related errors
                return jsonify({"err": "Invalid Authentication.",
                                "log": str(err)})
            except BadRequestKeyError as err:  # Handle file attachment error
                return jsonify({"err": "Please attach a file to the request",
                                "log": str(err)})
            except JSONDecodeError as err:  # Handle formatting related errors
                return jsonify({"err": "Incorrect formatting of data",
                                "log": str(err)})
            except ResponseError as err:
                return jsonify({"err": str(err),
                                "log": str(err)})
            
            finally:
                if os.path.exists(deposit_id):
                    os.remove(deposit_id)

        # Deletes one object i.e. a file from the specified bucket only.

        elif request.method == 'DELETE':
            try:
                # get data from request payload
                config = json.loads(request.form.get('config'))

                # extract bucket_name value
                bucket_name = config.get('bucket_name')

                # extract object specific deposit_id
                deposit_id = config.get('deposit_id')

                minioClient = create_client(request)

                if type(minioClient) == dict and 'err' in minioClient:
                    return jsonify(str(minioClient))
                # Check whether requested object exists
                error = minioClient.get_object(bucket_name, deposit_id)

                # Remove requested object from specified bucket
                rem_object = minioClient.remove_object(bucket_name, deposit_id)

            # except (NoSuchBucket, InvalidBucketError, ResponseError, TypeError) as err:  # Handle bucket_name related errors
            #     return jsonify({"err": "Bucket does not exist.",
            #                     "log": str(err)})
            # except NoSuchKey as err:  # Handle deposit_id related error
            #     return jsonify({"err": "Please enter valid deposit_id.",
            #                     "log": str(err)})
            # except (AccessDenied, InvalidAccessKeyId, SignatureDoesNotMatch) as err:  # Handle authentication related errors
            #     return jsonify({"err": "Invalid Authentication.",
            #                     "log": str(err)})
            # except JSONDecodeError as err:  # Handle formatting related errors
            #     return jsonify({"err": "Incorrect formatting of data",
            #                     "log": str(err)})

            except Exception as err:
                logging.error(f'DELETE err: {str(err)}')
                return jsonify({'err': str(err)})

            return jsonify({"deposit_id": deposit_id})

        else:
            return jsonify({
                "err": "Unsupported method.",
                "log": "Unsupported method."
            })

    # AT THIS ENDPOINT, EACH ACTION IS SPECIFIC TO A BUCKET AT IT'S CORE

    @app.route('/bucket', methods=['GET', 'POST', 'DELETE'])
    def bucket():

        # Get metadata of all or a list of objects in a specific bucket

        if request.method == 'GET':
            logging.info(f'/bucket GET: {request.form}')

            try:
                minioClient = create_client(request)

                if type(minioClient) == dict and 'err' in minioClient:
                    return jsonify(minioClient)

                config = json.loads(request.form.get('config'))
                bucket_name = config.get('bucket_name')

                objects = minioClient.list_objects(bucket_name, recursive=True)

                num_files = 0 
                bucket_size = 0
                largest_file_size = 0
                for obj in objects:
                    num_files += 1
                    bucket_size += obj.size
                    if obj.size > largest_file_size:
                        largest_file_size = obj.size
                return jsonify({
                    'bucket_size': bucket_size,
                    'num_files': num_files,
                    'largest_file': largest_file_size
                    })

            except NoSuchBucket as err:  # Handle bucket_name related errors
                return jsonify({"err": "Bucket does not exist.",
                                "log": str(err)})
            except (AccessDenied, InvalidAccessKeyId, SignatureDoesNotMatch) as err:  # Handle authentication related errors
                return jsonify({"err": "Invalid Authentication.",
                                "log": str(err)})
            except (InvalidBucketError, TypeError) as err:  # Handle bucket_name related errors
                return jsonify({"err": "Please enter a valid bucket_name.",
                                "log": str(err)})
            except JSONDecodeError as err:
                return jsonify({"err": "Incorrect formatting of data field.",
                                "log": str(err)})
            except ResponseError as err:
                return jsonify({"err": "Response Error",
                                "log": str(err)})

        # Create a new bucket that does not yet exist

        elif request.method == 'POST':
            # extract authentication details
            if minio_keys(request):
                auth = minio_keys(request)
                if "err" in auth:
                    return jsonify(auth)
            else:
                return jsonify({"err": "No authentication keys provided",
                                "log": str(err)})

            # Initialize minioClient with an endpoint and keys.
            try:
                # select endpoint
                minioClient = create_client(request)

                if type(minioClient) == dict and 'err' in minioClient:
                    return jsonify(minioClient)
                config = json.loads(request.form.get('config'))
                data = json.loads(request.form.get('data'))
                if data:
                    new_bucket_name = data.get('new_bucket_name')
                    minioClient.make_bucket(new_bucket_name)
                    return jsonify({"new_bucket_name": new_bucket_name})
                else:
                    return jsonify({"err": "Invalid request.",
                                    "log": "Invalid request."})
            except ResponseError as err:
                return jsonify({"err": str(err),
                                "log": str(err)})
            except (InvalidAccessKeyId, AccessDenied, SignatureDoesNotMatch) as err:  # Handle authentication related errors
                return jsonify({"err": "Invalid Authentication.",
                                "log": str(err)})
            except BucketAlreadyOwnedByYou as err:  # Handle pre-existing bucket_name error
                return jsonify({"err": str(err),
                                "log": str(err)})
            except JSONDecodeError as err:  # Handle formatting related errors
                return jsonify({"err": "Incorrect formatting of data field.",
                                "log": str(err)})
            except (InvalidBucketError, TypeError) as err:  # Handle bucket_name related errors
                return jsonify({"err": "Please enter a valid new_bucket_name.",
                                "log": str(err)})
            except Exception as err:
                return jsonify({"err": "General Exception",
                                "log": str(err)})

        elif request.method == 'DELETE':
            if minio_keys(request):
                auth = minio_keys(request)
                if "err" in auth:
                    return jsonify(auth)
            else:
                return jsonify({"err": "No authentication keys provided"})

            try:
                # select endpoint
                minioClient = create_client(request)

                if type(minioClient) == dict and 'err' in minioClient:
                    return jsonify(minioClient)

                if request.form.get('config'):
                    config = json.loads(request.form.get('config'))

                data = json.loads(request.form.get('data'))
                bucket_name = data.get('bucket_name')

                objects = minioClient.list_objects(bucket_name, recursive=True)

                count = 0
                for obj in objects:
                    count += 1

                if count != 0:
                    return jsonify({"err": "Cannot delete non-empty bucket.",
                                    "log": "Cannot delete non-empty bucket."})

                minioClient.remove_bucket(bucket_name)
                return jsonify({"bucket_name": str(bucket_name)})

            except ResponseError as err:
                return jsonify({"err": str(err),
                                "log": str(err)})
            except (InvalidAccessKeyId, AccessDenied, SignatureDoesNotMatch) as err:  # Handle authentication related errors
                return jsonify({"err": "Invalid Authentication.",
                                "log": str(err)})
            except BucketAlreadyOwnedByYou as err:  # Handle pre-existing bucket_name error
                return jsonify({"err": "This bucket is already created",
                                "log": str(err)})
            except JSONDecodeError as err:  # Handle formatting related errors
                return jsonify({"err": "Incorrect formatting of data field.",
                                "log": str(err)})
            except (InvalidBucketError, TypeError) as err:  # Handle bucket_name related errors
                return jsonify({"err": "Please enter a valid bucket_name.",
                                "log": str(err)})
            except NoSuchBucket as err:
                return jsonify({"err": "This bucket does not exist.",
                                "log": str(err)})

    # THIS ENDPOINT HANDLES METADATA AT OBJECT LEVEL

    @app.route('/metadata', methods=['GET'])
    def metadata():
        if request.method == 'GET':

            if minio_keys(request):
                auth = minio_keys(request)
                if "err" in auth:
                    return jsonify(auth)
            else:
                return jsonify({"err": "No authentication keys provided.",
                                "log": "No authentication keys provided."})

            # select endpoint
            minioClient = create_client(request)

            if type(minioClient) == dict and 'err' in minioClient:
                return jsonify({"err": str(minioClient)})

            config = json.loads(request.form.get('config'))

            deposit_id = config.get('deposit_id')
            bucket_name = config.get('bucket_name')

            try:
                obj = minioClient.get_object(bucket_name, deposit_id)
            except NoSuchKey as err:
                return jsonify({"err": "The requested deposit_id does not exist.",
                                "log": str(err)})
            except (AccessDenied, InvalidAccessKeyId, SignatureDoesNotMatch) as err:
                return jsonify({"err": "Invalid Authentication.",
                                "log": str(err)})

            # check whether object exists in the bucket
            meta_obj = minioClient.fget_object(bucket_name, object_name=deposit_id, file_path=deposit_id)
            ret_object = {
                "metadata": str(meta_obj.metadata),
                "deposit_id": str(meta_obj.object_name),
                "modified": str(meta_obj.last_modified),
                "etag": str(meta_obj.etag),
                "size": str(meta_obj.size),
                "content_type": str(meta_obj.content_type)
            }
            return jsonify(ret_object)

    return app
