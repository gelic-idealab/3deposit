FROM python:3.7

EXPOSE 5000

WORKDIR /app

COPY . /app
RUN pip install pipenv
RUN pipenv install

CMD ["pipenv", "run", "python", "minio-service.py"]
