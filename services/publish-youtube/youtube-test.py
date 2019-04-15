from google.oauth2 import service_account
import googleapiclient.discovery

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
SERVICE_ACCOUNT_FILE = '/Users/hywan/Downloads/service-account.json'
with open(SERVICE_ACCOUNT_FILE) as f:
    print(f.readlines())

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
response = youtube.videos().list(part=1).execute()

# print(credentials)
# print(dir(credentials))
# print(credentials.token)
# print(credentials.scopes)
# print(credentials.signer)
# print(youtube, dir(youtube))
print(youtube.videos(), dir(youtube.videos))
print(response)