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

@app.route('/database', methods=['GET', 'POST', 'DELETE'])
def database():
	try:
		databases = client.list_database_names()
		return jsonify({"databases": databases})
	except Exception as err:
		return jsonify({"err": str(err)})

# add batch get post and delete above


@app.route('/object', methods=['GET', 'POST', 'DELETE'])		# DONE - Change to "object" and "database"
def object():
	if request.method == 'POST':
		try:
			config = json.loads(request.form.get('config')) # also can call it "metadata_obj"
			data = json.loads(request.form.get('data'))
			db_name = config.get('db_name')
			object_id = data.get('object_id')
			posts = db_name.posts
			post_id = posts.insert_one(post).inserted_id
			return jsonify({"post_id": str(post_id)})		# keep this for relational mapping at gateway
		except Exception as err:				# Expand exception possibilities later
			return jsonify({"err": str(err)})

	if request.method == 'GET':
		try:
			config = json.loads(request.form.get('config'))
			db_name = config.get('db_name')
			object_id = data.get('object_id')
			db_name = client.MongoTest2
			posts = db_name.posts
			metadata_obj_iter = posts.find({"deposit_id":obj_id})		# How to find 2? Iterate? or is there a find_all?
			print(metadata_obj_iter)
			metadata_obj_iter_list = [i for i in metadata_obj_iter]
			num_metadata_objs = len(metadata_obj_iter_list)
			if num_metadata_objs > 1:
				#print("You have more than one 3D metadata object with the same deposit_id in your database! We are returning the most recently added metadata object back to you; however, you should seriously consider consolidating them...")

				list_of_objs_to_output = [jsonify({"metadata_obj": str(obj)}) for obj in metadata_obj_iter]
				print(list_of_objs_to_output)

				metadata_obj = metadata_obj_iter_list[-1] # this should reference the most recently added metadata_obj with the particular requested deposit_id
				return jsonify({"metadata_obj": str(metadata_obj)})

			else:
				metadata_obj = metadata_obj_iter_list[0]
				# metadata_obj = posts.find_one({"deposit_id":obj_id})
				return jsonify({"metadata_obj": str(metadata_obj)})

		except Exception as err:
			return jsonify({"err": str(err)})

	if request.method == 'DELETE':
		try:
			config = json.loads(request.form.get('config')) # also can call it "metadata_obj"
			data = json.loads(request.form.get('data'))
			db_name = config.get('db_name')
			object_id = data.get('object_id')
			db2 = client.MongoTest2
			posts = db2.posts
			del_obj = posts.delete_one({"deposit_id":obj_id})
			# If there are two documents with the same deposit_id (for instance, if one of them was inserted twice, creating a duplicate entry), then just one of them
			# is deleted (in the same order as when each was added--i.e., the first one that was added will be the first one that's deleted. I tested this out to see.)
			return jsonify({"del_obj": str(del_obj)})		# keep this for relational mapping at gateway
		except Exception as err:
			return jsonify({"err": str(err)})

if __name__ == '__main__':
	app.run(debug=True)

