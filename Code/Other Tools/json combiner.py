import os
import time
import json
import re

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

paths = []
dict = {}
for files in os.listdir("/home/musaddiq/Desktop/Combining Products/Products"):
	filepath = os.path.join("/home/musaddiq/Desktop/Combining Products/Products/", files)
	paths.append(filepath)
	
paths = natural_sort(paths)

for path in paths:
	with open(path, 'r') as f:
		JSON = json.load(f)
	dict.update(JSON)
	
print(len(dict))
print(json.dumps(dict, indent = 4))

with open("Combined", 'w') as f:
	json.dump(dict, f, indent = 2)

