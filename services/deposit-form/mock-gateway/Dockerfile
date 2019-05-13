# run 'docker build .' to build
# check for successful build with 'docker ps -a'

FROM python:3.7
COPY . /app
WORKDIR /app
EXPOSE 5000
RUN pip install pipenv
RUN pipenv install
