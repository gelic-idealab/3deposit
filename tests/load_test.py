import requests

count = 1
while True:
    r = requests.get('http://3deposit.library.illinois.edu/api/gallery')
    print(r, count)
    count += 1