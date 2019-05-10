import os
from google.oauth2 import service_account
import googleapiclient.discovery
from apiclient.http import MediaFileUpload

# API scope and credentials
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
SERVICE_ACCOUNT_FILE = 'C:\\Users\\rwwalla2\\Documents\\3deposit-service.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# create client
client = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

# create request
request = client.videos().insert(
        part="snippet,status",
        body={
              "snippet": {
                          "title": "My video title",
                          "description": "This is a description of my video",
                          "tags": ["cool", "video", "more keywords"],
                          "categoryId": 22
                        },
              "status": {
                         "privacyStatus": "public",
                         "embeddable": True,
                         "license": "youtube"
                        }
            },
        media_body=MediaFileUpload("sample.mp4")
    )
response = request.execute()

print(response)
