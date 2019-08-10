import requests
import json
from uuid import uuid4

url = "http://3deposit.library.illinois.edu/api/form/upload"
DEPOSIT_ID = str(uuid4())

querystring = {"resumableChunkNumber": "1", "resumableTotalChunks": "1", "deposit_id": DEPOSIT_ID}

f = open('test360.zip', 'rb')
files = {'file': f}

response = requests.request("POST", url, files=files, params=querystring)

print(response.text)
url = "http://3deposit.library.illinois.edu/api/form/submit"
payload_dict = { 
    'media_type': 'video',
    'id': DEPOSIT_ID,
    'form': [
        {
            'id': 'object_title',
            'value': 'Test 360 video'
        },
        {
            'id': 'media_type',
            'value': 'video'
        },
        {
            'id': 'description',
            'value': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
        },
        {
            'id': 'projection',
            'value': 'cylindrical'
        },
        {
            'id': 'stereo_format',
            'value': 'mono'
        },
        {
            'id': 'filename',
            'value': 'test360.mp4'
        }
    ]
}

payload = json.dumps(payload_dict)

response = requests.request("POST", url, data=payload)

print(response.text)
