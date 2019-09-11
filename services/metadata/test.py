import pymediainfo


m = pymediainfo.MediaInfo.parse("test360.mp4")

print(str(m.to_json()))
