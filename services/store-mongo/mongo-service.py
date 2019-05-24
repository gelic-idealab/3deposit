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

@app.route('/mongo_db', methods=['GET', 'POST', 'DELETE'])
def mongo_db():
	try:
		databases = client.list_database_names()
		return jsonify({"databases": databases})
	except Exception as err:
		return jsonify({"err": err})

# add batch get post and delete above


@app.route('/mongo_object', methods=['GET', 'POST', 'DELETE'])		# DONE - Change to "mongo_object" and "mongo_db"
def mongo_object():
	if request.method == 'POST':
		try:
			post = json.loads(request.form.get('data')) # also can call it "metadata_obj"
			db2 = client.MongoTest2		# rename these later too
			posts = db2.posts
			post_id = posts.insert_one(post).inserted_id
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

	if request.method == 'DELETE':
		try:
			obj_data = json.loads(request.form.get('data'))
			obj_id = obj_data.get('deposit_id')
			db2 = client.MongoTest2
			posts = db2.posts
			del_obj = posts.delete_one({"deposit_id":obj_id})		# If there are two documents with the same deposit_id (for instance, if one of them was inserted twice, creating a duplicate entry), then just one of them is deleted (in the same order as when each was added--i.e., the first one that was added will be the first one that's deleted. I tested this out to see.)
			return jsonify({"del_obj": str(del_obj)})		# keep this for relational mapping at gateway
		except Exception as err:
			return jsonify({"err": str(err)})

if __name__ == '__main__':
	app.run(debug=True)
