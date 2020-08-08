import time
import json
import os
import re


JSON = {}


with open('/home/mohammed/Desktop/Product List/Split/7.25%/Products List 7.25% 16.json', 'r') as f:
    JSON = json.load(f)

print(len(JSON))

from itertools import zip_longest

items1, items2 = zip(*zip_longest(*[iter(JSON.items())]*2))
d1 = dict(item for item in items1 if item is not None)
d2 = dict(item for item in items2 if item is not None)

print(len(d1))
print(len(d2))

with open('/home/mohammed/Desktop/Product List/Split/3.625%/Products List 3.625% 31.json', 'w') as f:
    f.write(json.dumps(d1, indent = 2))

with open('/home/mohammed/Desktop/Product List/Split/3.625%/Products List 3.625% 32.json', 'w') as f:
    f.write(json.dumps(d2, indent = 2))
