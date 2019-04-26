docker run -it -p 9000:9000 --name minio1 \
  -v C:\data:/data \
  -v C:\minio\config:/root/.minio \
  minio/minio server /data