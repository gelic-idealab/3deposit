import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

# https://api.mongodb.com/python/current/tutorial.html


DATABASE_NAME = 'deposits'
COLLECTION_NAME = 'metadata'
username = 'root'
password = 'example'

client = MongoClient('mongodb://{username}:{password}@localhost:27017/'.format(username=username, password=password))
database = client[DATABASE_NAME]
collection = database[COLLECTION_NAME]

app = Flask(__name__)

@app.route('/db', methods=['GET', 'POST', 'DELETE'])
def db():
	try:
		databases = client.list_database_names()
		return jsonify({"databases": databases})
	except Exception as err:
		return jsonify({"err": err})


@app.route('/object', methods=['GET', 'POST', 'DELETE'])		# Change to "mongo_object" and "mongo_db"
def object():
	if request.method == 'POST':
		try:
			post = json.loads(request.form.get('data')) # also can call it "metadata_obj"
			db2 = client.MongoTest2
			posts = db2.posts
			post_id = posts.insert_one(post).inserted_id
			# post_id
			return jsonify({"post_id": str(post_id)})		# keep this for relational mapping at gateway
		except Exception as err:				# Exapand exception possibilities later
			return jsonify({"err": str(err)})

	if request.method == 'GET':
		try:
			obj_data = json.loads(request.form.get('data'))
			obj_id = obj_data.get('deposit_id')
			db2 = client.MongoTest2
			posts = db2.posts
			metadata_obj = posts.find_one({"deposit_id":obj_id})		# How to find 2? Iterate? or is there a find_all?
			return jsonify({"metadata_obj": str(metadata_obj)})
		except Exception as err:
			return jsonify({"err": str(err)})


if __name__ == '__main__':
	app.run(debug=True)
