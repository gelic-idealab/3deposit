import os
import json
import requests
import vimeo
from flask import Flask, request, jsonify
from unpack.unpack import get_value

app = Flask(__name__)

@app.route("/vimeo", methods=["POST", "GET", "DELETE"])
def vimeo_service():
    api = get_value(request, "config", "api")
    access_token = get_value(request, "config", "access_token")
    client_id = get_value(request, "config", "client_id")
    client_secret = get_value(request, "config", "client_secret")
    client = vimeo.VimeoClient(
        token=access_token,
        key=client_id,
        secret=client_secret
    )

    if request.method == "POST":
        try:
            cc_license = get_value(request, "data", "license")
            comments = get_value(request, "data", "comments")
            description = get_value(request, "data", "description")
            embed = get_value(request, "data", "embed")
            filename = get_value(request, "data", "filename")
            name = get_value(request, "data", "name")
            projection = get_value(request, "data", "projection")
            stereo_format = get_value(request, "data", "stereo_format")
            view = get_value(request, "data", "view")
            file = request.files.get("file")
            if file and filename:
                file.save(filename)
                uri = client.upload(filename, data={
                    "description": description,
                    "name": name,
                    "license": cc_license
                })
                client.patch(uri, data={
                    "privacy": {
                        "comments": comments,
                        "embed": embed,
                        "view": view
                    },
                    "spatial": {
                        "projection": projection,
                        "stereo_format": stereo_format
                    }
                })
                os.remove(filename)
                return jsonify({"res": {"uri": uri}})
            else:
                return jsonify({"err": "No file provided"})
        except Exception as err:
            return jsonify({"err": str(err)})

    elif request.method == "GET":
        try:
            get_data = {}
            get_videos = client.get(api + "/me/videos").json()
            get_data["videos"] = get_videos
            get_num_videos = get_data["videos"]["total"]
            get_video_data = get_data["videos"]["data"]
            if get_num_videos > 0:
                for get_video_num in range(get_num_videos):
                    get_video = get_video_data[get_video_num]
                    get_video_id = get_video["uri"].split("/")[2]
                    get_comments = client.get(api + "/videos/" + get_video_id + "/comments").json()
                    get_video["comments"] = get_comments
                    get_num_comments = get_video["comments"]["total"]
                    get_comment_data = get_video["comments"]["data"]
                    if get_num_comments > 0:
                        for get_comment_num in range(get_num_comments):
                            get_comment = get_comment_data[get_comment_num]
                            get_comment_id = get_comment["uri"].split("/")[4]
                            get_replies = client.get(api + "/videos/" + get_video_id + "/comments/" + get_comment_id + "/replies").json()
                            get_comment["replies"] = get_replies
            return jsonify({"res": get_data})
        except Exception as err:
            return jsonify({"err": str(err)})

    elif request.method == "DELETE":
        try:
            delete_data = {}
            delete_videos = client.get(api + "/me/videos").json()
            delete_data["videos"] = delete_videos
            delete_num_videos = delete_data["videos"]["total"]
            if delete_num_videos > 0:
                delete_video_data = delete_data["videos"]["data"]
                delete_video_ids_list = []
                delete_video_ids_str = ""
                for delete_video_num in range(delete_num_videos):
                    delete_video = delete_video_data[delete_video_num]
                    delete_video_id = delete_video["uri"].split("/")[2]
                    delete_video_ids_list.append(delete_video_id)
                    if delete_num_videos == 1:
                        delete_video_ids_str = delete_video_ids_str + delete_video_id
                    elif delete_num_videos == 2:
                        if delete_video_num == 0:
                            delete_video_ids_str = delete_video_ids_str + delete_video_id + " or "
                        else:
                            delete_video_ids_str = delete_video_ids_str + delete_video_id
                    else:
                        if delete_video_num < delete_num_videos - 1:
                            delete_video_ids_str = delete_video_ids_str + delete_video_id + ", "
                        else:
                            delete_video_ids_str = delete_video_ids_str + "or " + delete_video_id
                delete_input_video_id = str(input("Do you wish to delete video #" + delete_video_ids_str + " and/or its comments (if any)? To proceed, enter the ID of the video you wish to delete: "))
                if delete_input_video_id in delete_video_ids_list:
                    delete_comments = client.get(api + "/videos/" + delete_input_video_id + "/comments").json()
                    delete_video["comments"] = delete_comments
                    delete_num_comments = delete_video["comments"]["total"]
                    if delete_num_comments > 0:
                        delete_comment_data = delete_video["comments"]["data"]
                        delete_comment_ids_list = []
                        delete_comment_ids_str = ""
                        for delete_comment_num in range(delete_num_comments):
                            delete_comment = delete_comment_data[delete_comment_num]
                            delete_comment_id = delete_comment["uri"].split("/")[4]
                            delete_comment_ids_list.append(delete_comment_id)
                            if delete_num_comments == 1:
                                delete_comment_ids_str = delete_comment_ids_str + delete_comment_id
                            elif delete_num_comments == 2:
                                if delete_comment_num == 0:
                                    delete_comment_ids_str = delete_comment_ids_str + delete_comment_id + " or "
                                else:
                                    delete_comment_ids_str = delete_comment_ids_str + delete_comment_id
                            else:
                                if delete_comment_num < delete_num_comments - 1:
                                    delete_comment_ids_str = delete_comment_ids_str + delete_comment_id + ", "
                                else:
                                    delete_comment_ids_str = delete_comment_ids_str + "or " + delete_comment_id
                        delete_input_select = str(input("This video has comment(s). Do you wish to 1) delete the video and its comment(s) or 2) just the comment(s)? Enter \"1\" or \"2\" to proceed: "))
                        if delete_input_select == "1":
                            client.delete(api + "/videos/" + delete_input_video_id)
                            return jsonify({"res": "Video deleted successfully"})
                        elif delete_input_select == "2":
                            delete_input_comment_id = str(input("Do you wish to delete comment #" + delete_comment_ids_str + "? To proceed, enter the ID of the video you wish to delete: "))
                            if delete_input_comment_id in delete_comment_ids_list:
                                client.delete(api + "/videos/" + delete_input_video_id + "/comments/" + delete_input_comment_id)
                                return jsonify({"res": "Comment deleted successfully"})
                            else:
                                return jsonify({"res": "No answer given or incorrect answer"})
                        else:
                            return jsonify({"res": "No answer given or incorrect answer"})   
                    else:
                        delete_input_select_none = str(input("This video does not have any comments. Do you wish to delete it? Enter \"Y\" to proceed: "))
                        if delete_input_select_none == "Y":
                            client.delete(api + "/videos/" + delete_input_video_id)
                            return jsonify({"res": "Video deleted successfully"})
                        else:
                            return jsonify({"res": "No answer given or incorrect answer"})
                else:
                    return jsonify({"res": "No answer given or incorrect answer"})
            else:
                return jsonify({"res": "No video to delete"})
        except Exception as err:
            return jsonify({"err": str(err)})

if __name__ == "__main__":
    app.run(debug=True)
