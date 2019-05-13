FROM python:3.7
COPY . /gateway
WORKDIR /gateway
EXPOSE 8080
RUN pip install pipenv && pipenv install
# CMD ["pipenv", "run", "python", "init_db.py"]