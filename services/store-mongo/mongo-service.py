import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

# https://api.mongodb.com/python/current/tutorial.html


DATABASE_NAME = 'deposits'
username = 'root'
password = 'example'

client = MongoClient('mongodb://{username}:{password}@localhost:27017/'.format(username=username, password=password))
database = client[DATABASE_NAME]

app = Flask(__name__)

@app.route('/db', methods=['GET', 'POST', 'DELETE'])
def db():
    try:
        databases = client.list_database_names()
        return jsonify({"databases": databases})
    except Exception as err:
        return jsonify({"err": err})


if __name__ == '__main__':
    app.run(debug=True)