import requests
import json
from uuid import uuid4

url = "http://localhost/api/form/upload"
DEPOSIT_ID = str(uuid4())

querystring = {"resumableChunkNumber": "1", "resumableTotalChunks": "1", "deposit_id": DEPOSIT_ID}

f = open('a-frame.zip', 'rb')
files = {'file': f}

headers = {
    'User-Agent': "PostmanRuntime/7.15.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "7b7151ab-d4f0-4179-aaea-b22c2f60b587,681044ad-d0af-468f-b64b-344adfe462cb",
    'Host': "localhost:8080",
    'accept-encoding': "gzip, deflate",
    'content-length': "29096",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("POST", url, files=files, headers=headers, params=querystring)

print(response.text)
url = "http://localhost/api/form/submit"
payload_dict = { 
    'media_type': 'vr',
    'id': DEPOSIT_ID,
    'form': [
        {
            'id': 'object_title',
            'value': 'VR Scene'
        },
        {
            'id': 'media_type',
            'value': 'vr'
        },
        {
            'id': 'description',
            'value': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
        }
    ]
}

payload = json.dumps(payload_dict)
headers = {
    'Content-Type': "application/json",
    'User-Agent': "PostmanRuntime/7.15.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "0f5b41a0-d7a5-4587-9a1d-ee8aed8da8e4,5cb528e4-b861-432a-bfa8-b0c6bb2c3461",
    'Host': "localhost:8080",
    'accept-encoding': "gzip, deflate",
    'content-length': "185",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)
