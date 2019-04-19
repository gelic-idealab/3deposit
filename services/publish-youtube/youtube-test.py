from google.oauth2 import service_account
import googleapiclient.discovery
from apiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
SERVICE_ACCOUNT_FILE = 'C:\\Users\\rwwalla2\\Documents\\youtube_api_auth.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

body = {
        "snippet": {
        "categoryId": "22",
        "description": "Description of uploaded video.",
        "title": "Test video upload."
        },
        "status": {
                "privacyStatus": "private"
                }
        }

fileloc = 'test.mp4'

upload = client.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(fileloc, chunksize=-1)
  )

retry = 0
while retry < 10:
        try:
                upload.execute()
        except Exception as e:
                print(e)
                retry += 1
