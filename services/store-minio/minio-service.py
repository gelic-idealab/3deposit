from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

OBJECT_PATH = 'test_object.zip'

# Initialize minioClient with an endpoint and keys.
minioClient = Minio('localhost:9000',
                    access_key='AKIAIOSFODNN7GRAINGER',
                    secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY',
                    secure=False)

try:
    print(minioClient.fput_object('3deposit', OBJECT_PATH, OBJECT_PATH))
except ResponseError as err:
    print(err)
