import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient

# https://api.mongodb.com/python/current/tutorial.html


DATABASE_NAME = '3deposit'
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

@app.route('/database', methods=['GET', 'POST', 'DELETE'])
def database():
    try:
        databases = client.list_database_names()
        return jsonify({"databases": databases})
    except Exception as err:
        return jsonify({"err": str(err)})

# TO DO: Add Get, Post, and Delete request methods above


@app.route('/object', methods=['GET', 'POST', 'DELETE'])
def object():
    if request.method == 'POST':
        """ POST process for posting a metadata object to the Mongo Database.

            Method [should later] receives service request containing "data"
            and "config" keys, in the format of 'service_api.json'.

            First checks database to make sure no objects with the given
            deposit_id already exist, and if not, then posts it to the DB.

            :return post_id: Unique id for posted object, assigned by MongoDB,
                             returned as a string. Note that this ID is not
                             the same as the 'deposit_id'.
        """

        try:
            # config = json.loads(request.form.get('config'))
            # db_name = config.get('db_name')
            db_name = client.MongoTest2
            config = json.loads(request.form.get('config'))
            #data = json.loads(request.form.get('data'))
            
            deposit_id = config.get('deposit_id')
            posts = db_name.posts
            
            # Make sure an object with the deposit ID doesn't already exist
            if posts.find_one({"deposit_id":deposit_id}):
                return jsonify({"err":("A metadata object with that deposit_id"
                                        " already exists.") })
            else:
                post_id = posts.insert_one(data).inserted_id
                return jsonify({"post_id": str(post_id)})

        except Exception as err:
            return jsonify({"err": str(err)})


    if request.method == 'GET':
        """ GET process for retrieving a metadata object to the Mongo Database.

            Method [should later] receives service request containing "data"
            and "config" keys, in the format of 'service_api.json'.

            Process first performs a "find all" on the database for objects
            with the given 'deposit_id', and if there are more than one,
            returns an error along with a list of all the metadata objects
            with that particular deposit_id as well as the one that was most
            recently added to the database. If only one exists, then that one
            is returned.

            :return metadata_obj: All data associated with the metadata object
                                  with the specified 'deposit_id', returned as
                                  a json object with the metadata as the value
                                  and formatted as a string.
        """

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

                most_recent_metadata_obj = metadata_obj_iter_list[-1]

                return jsonify({
                    "err":( "You have more than one 3D metadata object with "
                            "the same deposit_id in your database! We are "
                            "returning a list of these objects back to you; "
                            "however, you should consolidate them." ),
                    "list_of_metadata_objs": list_of_metadata_objs,
                    "most_recent_metadata_obj": str(most_recent_metadata_obj)
                     })

            else:
                metadata_obj = posts.find_one({"deposit_id":deposit_id})
                return jsonify({"metadata_obj": str(metadata_obj)})

        except Exception as err:
            return jsonify({"err": str(err)})

    if request.method == 'DELETE':
        """ Process for deleting a metadata object to the Mongo Database.

            Method [should later] receives service request containing "data"
            and "config" keys, in the format of 'service_api.json'.

            Process performs a "delete one" on the database for an object
            with the given 'deposit_id'.

            If there are >1 documents with the same deposit_id (for
            instance, if one of them was inserted twice, creating a
            duplicate entry), then just one of them is deleted (in
            the same order as when each was added--i.e., the first
            one that was added will be the first one that's deleted.

            :return del_obj: pymongo.results.DeleteResult object for the
                             deleted metadata object of the given 'deposit_id'
                             (formatted as a string).
        """

        try:
            # config = json.loads(request.form.get('config'))
            # db_name = config.get('db_name')
            db_name = client.MongoTest2
            data = json.loads(request.form.get('data'))
            deposit_id = data.get('deposit_id')
            posts = db_name.posts
            del_obj = posts.delete_one({"deposit_id": deposit_id})

            return jsonify({"del_obj": str(del_obj)})

        except Exception as err:
            return jsonify({"err": str(err)})

if __name__ == '__main__':
    app.run(debug=True)
