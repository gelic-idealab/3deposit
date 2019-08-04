FROM python:3.7-slim
COPY . /gateway
WORKDIR /gateway
EXPOSE 8080
RUN pip install pipenv && pipenv install