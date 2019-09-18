from pymediainfo import MediaInfo as mi
import subprocess
# import pymediainfo
# from metadata_utils import *
import pprint
import json

m = mi.parse("test360_orig.mp4")
# m = parse_mpeg4("test360.mp4")


# for track in m.tracks:
#     if track.track_type == 'Video':
#         print(track.bit_rate, track.bit_rate_mode, track.codec)

# m_json = m.to_json()
m_dict = m.to_data()
pprint.pprint(m_dict['tracks'])

get_360_info = subprocess.run(["./Image-ExifTool-11.65/exiftool", "-a", "-u", "-g1", "test360_orig.mp4"], stdout=subprocess.PIPE)
output_360_info = str(get_360_info.stdout)
spherical_start = output_360_info.find('XMP-GSpherical') + len('XMP-GSpherical ----')
# spher_start += len('XMP-GSpherical ----')
spherical_end = output_360_info.find('----', spherical_start)
spherical_data_extract = output_360_info[spherical_start : spherical_end]
spherical_data = spherical_data_extract.split('\\n')
spherical_data_clean = [i.replace(' ','') for i in spherical_data[1:-1]]

print("\nSpherical Metadata:")
for s in spherical_data_clean:
    print(s)


exit()
# for i in m_json:
#     print(str(i))

# print(str(m.to_json()))

# To get projection and other 360 info, might want to use this tool from GitHub:
# https://github.com/google/spatial-media
# Only problem (I think) is that it may only run with python 2.7


"""

    ./Image-ExifTool-11.65/exiftool -a -u -g1 360_VR_orig2.mp4


    >>> from libxmp import XMPFiles, consts
    >>> xmpfile = XMPFiles(file_path="./testVimeo360.mp4", open_forupdate=True)
    >>> xmp = xmpfile.get_xmp()
    >>> print(xmp)




    >>> uuid.UUID(id)
    UUID('be7acfcb-97a9-42e8-9c71-999491e3afac')
    >>> uid = uuid.UUID(id)
    >>> uid.bytess
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: 'UUID' object has no attribute 'bytess'
    >>> uid.bytes
    b'\xbez\xcf\xcb\x97\xa9B\xe8\x9cq\x99\x94\x91\xe3\xaf\xac'
    >>> with open('./test360_orig.mp4','rb') as r:
    ...     for l in r.read():
    ...             if l==uid.bytes:
    ...                     print("Hooray!")
    ...

    >>>
    >>> with open('./test360_orig.mp4','rb') as r:
    ...     s = r.read()
    ... s.find(uid.bytes)
      File "<stdin>", line 3
        s.find(uid.bytes)
        ^
    SyntaxError: invalid syntax
    >>> with open('./test360_orig.mp4','rb') as r:
    ...     s = r.read()
    ...
    >>> s.find(uid.bytes)
    -1
    >>> s.find(b'\xbez\xcf\xcb\x97\xa9B\xe8\x9cq\x99\x94\x91\xe3\xaf\xac')
    -1
    >>> if s.find(b'\xbez\xcf\xcb\x97\xa9B\xe8\x9cq\x99\x94\x91\xe3\xaf\xac'):
    ...     print("YES")
    ... else:
    ...     print("NO")
    ...
    YES
"""
