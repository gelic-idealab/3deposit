import os
import json
import logging
import zipfile
import subprocess

from flask import Flask, request, jsonify
import pymediainfo
from pymediainfo import MediaInfo as mi
# https://pymediainfo.readthedocs.io/en/stable/


'''
Flask app that generates & harvests metadata from 3d media,
handles POST requests with media payload, responds with metadata.
'''

app = Flask(__name__)

# logging boilerplate
service_name = str(os.path.basename(__file__))
logfile = 'service.log'
logging.basicConfig(level=logging.DEBUG, filename=logfile)
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info(f'Starting {service_name}...')

@app.route('/log', methods=['GET'])
def log_handler():
    try:
        with open(logfile, 'r') as f:
            resp = f.read()
            return jsonify({'logfile': str(resp)})
    except Exception as err:
        return jsonify({'err': str(err)})


@app.route('/', methods=['POST', 'GET'])
def handler():

    if request.method == 'POST':

        try:
            # unpack request data
            data = json.loads(request.form.get('data'))
            did = data.get('deposit_id')
            deposit_form_metadata = data.get('metadata')

            logging.info(f"POST request for deposit_id: {did}, data: {deposit_form_metadata}")

            # unzip file payload
            file = request.files.get('file')
            if file and did:
                fzip = did
                file.save(fzip)

                with zipfile.ZipFile(fzip, 'r') as zip_ref:
                    filename_360_video = zip_ref.namelist()[0]
                    logging.debug(f'filename_360_video: {filename_360_video}')
                    zip_ref.extract(filename_360_video)

                # extract metadata and return
                # exiftool_dir = '/path/to/exiftool/toplevel/directory/Image-ExifTool-11.65'
                exiftool_dir = 'Image-ExifTool-11.65'

                mediainfo_metadata = get_mediainfo_metadata(filename_360_video)
                spherical_metadata = get_360_metadata(filename_360_video, exiftool_dir)

                metadata_dict = {}

                if mediainfo_metadata is not None:
                    metadata_dict.update( mediainfo_metadata )

                if spherical_metadata is not None:
                    metadata_dict.update( {len(metadata_dict) : spherical_metadata} ) # len(metadata_dict) determines the next key/index to use

                if mediainfo_metadata is None and spherical_metadata is None:
                    return jsonify({"err": "No media metadata information was found for this file."})

                return jsonify({"deposit_id": did, "video_metadata": metadata_dict})


        except Exception as err:
            logging.error(str(err))
            return jsonify({'err': str(err)})

        finally:
            if os.path.exists(did):
                os.remove(did)
            if os.path.exists(filename_360_video):
                os.remove(filename_360_video)


def get_mediainfo_metadata(media_file):
    """
    Function to extract the general video and audio metadata from a media file (e.g., MP4).
    This function makes use of the MediaInfo library via the 'pymediainfo' Python package.

    # For Later:
    May want to use "track_type, index" as keys later, since that would be useful to users
    to see what type of track each index represents (e.g., "General 0," "Video 1," "Audio 2").
        E.g.:   md_dict.update( { (temp_track_id, track.track_type) : d } )


    :param media_file: Path and filename of the media file (e.g., an MP4 file) from which
                       to extract MediaInfo metadata.

    :return md_dict: Dictionary of mediainfo metadata for the given media file, if existent.
                     Otherwise, return None.
    """

    try:
        m = mi.parse(media_file)

        md_dict = {}

        for (index, track) in enumerate(m.tracks):
            d = track.to_data()
            md_dict.update( { index : d } )

        return md_dict

    except:
        return None


def get_360_metadata(mp4_file, path_to_exif_toolkit):
    """
    Function to gather 360 spherical metadata from an MP4 file. This function uses the ExifTool
    kit/package created by Phil Harvey: https://www.sno.phy.queensu.ca/~phil/exiftool/

    :param mp4_file: Path and filename of a 360 MP4 file from which to extract metadata.
    :param path_to_exif_toolkit: Path to the ExifTool directory installed on your machine.
                                 Should be named something like, "Image-ExifTool-11.65".

    :return spherical_data_dict: Dictionary of sphereical metadata parameters and their values
                                 for the given MP4 file, if existent. Otherwise, returns None.
    """

    exiftool_exe = os.path.join(path_to_exif_toolkit, 'exiftool' )

    get_360_info = subprocess.run( [exiftool_exe, "-a", "-u", "-g1", mp4_file], stdout=subprocess.PIPE)

    output_360_info = str(get_360_info.stdout)

    try:
        spherical_start = output_360_info.find('XMP-GSpherical') + len('XMP-GSpherical ----')
        spherical_end = output_360_info.find('----', spherical_start)
        spherical_data_extract = output_360_info[spherical_start : spherical_end]
        spherical_data = spherical_data_extract.split('\\n')
        spherical_data_clean = [i.replace(' ','') for i in spherical_data[1:-1]]

        spherical_data_dict = {}
        for s in spherical_data_clean:
            s_k = s.split(':')[0]
            s_v = s.split(':')[1]
            spherical_data_dict.update( {s_k : s_v} )

        spherical_data_dict.update( {"track_type" : "XMP-GSpherical"} )

        return spherical_data_dict

    except:
        return None


if __name__ == '__main__':
    app.run()
