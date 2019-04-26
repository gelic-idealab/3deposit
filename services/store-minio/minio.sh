docker run -it -p 9000:9000 --name minio1 \
  -v minio_data:/data \
  -v minio_config:/root/.minio \
  minio/minio server /data