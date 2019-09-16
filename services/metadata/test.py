from pymediainfo import MediaInfo as mi
# import pymediainfo
import pprint
import json

# m = pymediainfo.MediaInfo.parse("test360.mp4")
m = mi.parse("test360.mp4")

for track in m.tracks:
    if track.track_type == 'Video':
        print(track.bit_rate, track.bit_rate_mode, track.codec)

m_json = m.to_json()
m_dict = m.to_data()
pprint.pprint(m_dict['tracks'])

exit()
for i in m_json:
    print(str(i))

# print(str(m.to_json()))

# To get projection and other 360 info, might want to use this tool from GitHub:
# https://github.com/google/spatial-media
# Only problem (I think) is that it may only run with python 2.7
