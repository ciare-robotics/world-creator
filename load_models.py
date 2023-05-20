import json
import pprint

with open('output_models.json', 'r') as f:
    worlds = json.load(f)

print(len(worlds))

only_description = []
for w in worlds:
    only_description.append({
        "name": w['name'],
        "tags": w.get('tags'),
        
        })
    

with open('output_models_name.json', 'w+') as file:
    file.write(json.dumps(only_description) + '\n')

print(len(only_description))
