docker run -it -p 9000:9000 --name minio1 \
  -v minio_data:/data \
  -v minio_config:/root/.minio \
  -e "MINIO_ACCESS_KEY=AKIAIOSFODNN7GRAINGER" \
  -e "MINIO_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYGRAINGERKEY" \
  minio/minio server /data