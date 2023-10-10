import json


rewrites = json.load(open("cleaned_rewrites.json", "r"))

for code in rewrites:
    print(code)
    print(rewrites[code]['code'])
    print()