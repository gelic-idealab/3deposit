import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

# https://api.mongodb.com/python/current/tutorial.html


DATABASE_NAME = 'deposits'
COLLECTION_NAME = 'metadata'
username = 'root'
password = 'example'

client = MongoClient(
    'mongodb://{username}:{password}@localhost:27017/'.format(
        username=username,
        password=password)
    )
database = client[DATABASE_NAME]
collection = database[COLLECTION_NAME]

app = Flask(__name__)

@app.route('/databases', methods=['GET', 'POST', 'DELETE'])
def databases():
    try:
        databases = client.list_database_names()
        return jsonify({"databases": databases})
    except Exception as err:
        return jsonify({"err": str(err)})

# TO DO: Add Get, Post, and Delete request methods above


@app.route('/objects', methods=['GET', 'POST', 'DELETE'])
def objects():
    if request.method == 'POST':
        try:
            client = create_client(request)
            # config = json.loads(request.form.get('config'))
            # db_name = config.get('db_name')
            db_name = client.MongoTest2
            data = json.loads(request.form.get('data'))
            deposit_id = data.get('deposit_id')
            posts = db_name.posts
            post_id = posts.insert_one(data).inserted_id
            return jsonify({"post_id": str(post_id)})

        except Exception as err:
            return jsonify({"err": str(err)})

    if request.method == 'GET':
        try:
            # config = json.loads(request.form.get('config'))
            # db_name = config.get('db_name')
            db_name = client.MongoTest2
            data = json.loads(request.form.get('data'))
            deposit_id = data.get('deposit_id')
            posts = db_name.posts
            metadata_obj_iter = posts.find({"deposit_id":deposit_id})
            metadata_obj_iter_list = [i for i in metadata_obj_iter]
            num_metadata_objs = len(metadata_obj_iter_list)

            if num_metadata_objs > 1:
                list_of_metadata_objs = [
                    str('{"metadata_obj": ' + str(obj) + '}')
                    for obj in metadata_obj_iter_list ]

                # Assign the most recently added 3D metadata object with the
                # particular deposit_id of interest to "most_recent_metadata_obj"
                most_recent_metadata_obj = metadata_obj_iter_list[-1]

                return jsonify({
                    "err":"You have more than one 3D metadata object with the \
                      same deposit_id in your database! We are returning a list \
                      of these objects back to you; however, you should consider \
                      consolidating them...",
                    "list_of_metadata_objs": list_of_metadata_objs,
                    "most_recent_metadata_obj": str(most_recent_metadata_obj)
                     })
            else:
                metadata_obj = metadata_obj_iter_list[0]
                # metadata_obj = posts.find_one({"deposit_id":deposit_id})
                return jsonify({"metadata_obj": str(metadata_obj)})

        except Exception as err:
            return jsonify({"err": str(err)})

    if request.method == 'DELETE':
        try:
            # config = json.loads(request.form.get('config'))
            # db_name = config.get('db_name')
            db_name = client.MongoTest2
            data = json.loads(request.form.get('data'))
            deposit_id = data.get('deposit_id')
            posts = db_name.posts
            del_obj = posts.delete_one({"deposit_id": deposit_id})

            # NOTE: If there are >1 documents with the same deposit_id
            # (for instance, if one of them was inserted twice,
            # creating a duplicate entry), then just one of them
            # is deleted (in the same order as when each was added
            # --i.e., the first one that was added will be the first
            # one that's deleted.)

            return jsonify({"del_obj": str(del_obj)})
        except Exception as err:
            return jsonify({"err": str(err)})

if __name__ == '__main__':
    app.run(debug=True)
