import requests

count = 1
while True:
    r = requests.get('https://3deposit.library.illinois.edu/api/gallery')
    print(r, count)
    count += 1