import os
from pymediainfo import MediaInfo as mi
import subprocess
import pprint
import json


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



video_file_360 = 'test360_orig.mp4'
exiftool_dir = '/home/piehld/Dropbox/Work/GA_Grainger/IdeaLab/3deposit/services/metadata/Image-ExifTool-11.65'

mediainfo_metadata = get_mediainfo_metadata(video_file_360)
spherical_metadata = get_360_metadata(video_file_360, exiftool_dir)

metadata_dict = {}

if mediainfo_metadata is not None:
    metadata_dict.update( mediainfo_metadata )

if spherical_metadata is not None:
    metadata_dict.update( {len(metadata_dict) : spherical_metadata} ) # len(metadata_dict) determines the next key/index to use

metadata_json = json.dumps(metadata_dict)

pprint.pprint(json.loads(metadata_json))
