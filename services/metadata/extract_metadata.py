import os
from pymediainfo import MediaInfo as mi
import subprocess
import pprint
import json

m = mi.parse("test360_orig.mp4")

md_dict = {}
for (index, track) in enumerate(m.tracks):

    # print(index, track)
    # if track.track_id == None:
    #     temp_track_id = 0
    # else:
    #     temp_track_id = track.track_id
    d = track.to_data()
    # d = track.to_json()

    # May want to use "track_type, index" as keys later, since that would be useful to users
    # to see what type of track each index represents (e.g., "General 0," "Video 1," "Audio 2").
    # md_dict.update( { (temp_track_id, track.track_type) : d } )

    md_dict.update( { index : d } )

    # print(track.bit_rate, track.bit_rate_mode, track.codec)

# pprint.pprint(md_dict)

# print(len(md_dict))
# exit()

def get_360_metadata(mp4_file, path_to_exif_toolkit):
    """
    Function to gather 360 spherical metadata from an MP4 file. This function uses the ExifTool
    kit/package created by Phil Harvey: https://www.sno.phy.queensu.ca/~phil/exiftool/

    :param mp4_file: path and filename of a 360 MP4 file from which to extract metadata.
    :param path_to_exif_toolkit: path to the ExifTool directory installed on your machine.
                                 Should be named something like, "Image-ExifTool-11.65".

    :return spherical_data_dict: Dictionary of sphereical metadata parameters and their values.
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

spherical_metadata = get_360_metadata('test360_orig.mp4', '/home/piehld/Dropbox/Work/GA_Grainger/IdeaLab/3deposit/services/metadata/Image-ExifTool-11.65')

# print("\nSpherical Metadata:")
# for s in spherical_metadata:
#     print(s,spherical_metadata[s])
#
# spherical_metadata_json = json.dumps(spherical_metadata)
# print(spherical_metadata_json)
# print(type(spherical_metadata_json))
# exit()

md_dict.update( {len(md_dict) : spherical_metadata} )

# pprint.pprint(md_dict)
# exit()

md_json = json.dumps(md_dict)
pprint.pprint(json.loads(md_json))

# for j in md_json:
#     pprint.pprint(j)
# exit()
# for i in m_json:
#     print(str(i))

# print(str(m.to_json()))
