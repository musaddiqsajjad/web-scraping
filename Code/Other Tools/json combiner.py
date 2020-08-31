import os
import time
import json
import re

sourcepath = ""   #change as needed
outputpath = ""   #change as needed

outputpath += "/out.json"   #output filename

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

paths = []
dict = {}
for files in os.listdir(sourcepath):
	filepath = os.path.join(sourcepath, files)
	paths.append(filepath)
	
paths = natural_sort(paths)

for path in paths:
	with open(path, 'r') as f:
		JSON = json.load(f)
	dict.update(JSON)

with open(outputpath, 'w') as f:
	json.dump(dict, f, indent = 2)

