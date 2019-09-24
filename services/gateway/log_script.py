import os

with open('./data/gateway.log', 'r') as f:
    l = f.read()
    ll = l.split('\n')

print(ll)
