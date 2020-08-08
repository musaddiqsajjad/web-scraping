import time
import json
import os
import re

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

JSON = {}
paths = []
bigdict = {}

for file in os.listdir('/home/musaddiq/Desktop/Product List/Products List'):
    if file.startswith("Products List"):
        filePath = os.path.join("/home/musaddiq/Desktop/Product List/Products List", file)
        paths.append(filePath)

paths = natural_sort(paths)

print(*paths, sep = "\n")

i = 0
for path in paths:
    #load productsList JSON into memory
    with open(path, 'r') as f:
        JSON = json.load(f)

    bigdict.update(JSON)
    i+=1
    print(i)

print(json.dumps(bigdict, indent = 2))

uniquebigdict = {}
seen = []

j = 0
d = 0
for key in bigdict:
        print(j)
        j+=1
        if bigdict[key]['URL'] not in seen:
            seen.append(bigdict[key]['URL'])
            uniquebigdict[key] = (bigdict[key])
        else:
            d+=1
            print(f"Duplicate Found! {d}")
            continue


print(f"Duplicates = {d}")
print(f"Unqiue = {len(uniquebigdict)}")

with open("/home/musaddiq/Desktop/Product List/bigProductList.json", 'w') as file:
    json.dump(uniquebigdict, file, indent = 2)
