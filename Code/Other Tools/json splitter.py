import time
import json
import os
import re


JSON = {}

sourcefile = ""
outputfile1 = ""
outputfile2 = ""

with open(sourcefile, 'r') as f:
    JSON = json.load(f)

print(len(JSON))

from itertools import zip_longest

items1, items2 = zip(*zip_longest(*[iter(JSON.items())]*2))
d1 = dict(item for item in items1 if item is not None)
d2 = dict(item for item in items2 if item is not None)

with open(outputfile1, 'w') as f:
    f.write(json.dumps(d1, indent = 2))

with open(outputfile2, 'w') as f:
    f.write(json.dumps(d2, indent = 2))
