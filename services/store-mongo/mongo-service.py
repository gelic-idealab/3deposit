import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

# https://api.mongodb.com/python/current/tutorial.html


DATABASE_NAME = 'deposits'

client = MongoClient('mongodb://localhost:27017/')
db = client[DATABASE_NAME]

app = Flask(__name__)

@app.route('/db', methods=['GET', 'POST', 'DELETE'])
def db():
    try:
        databases = client.list_database_names()
        return jsonify({"databases": databases})
    except Exception as err:
        return jsonify({"err": err})


if __name__ == '__main__':
    app.run()