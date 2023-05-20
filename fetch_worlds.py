import requests
import json

url = 'https://fuel.gazebosim.org/1.0/worlds'
params = {'page': 1}
response = requests.get(url, params=params)
response_data = response.json()
worlds = []

while True:
    response = requests.get(url, params=params)
    response_data = response.json()

    if type(response_data) != list:
        print("Response with 'Page not found' received.")
        break

    worlds.extend(response_data)

    params['page'] += 1

with open('output.txt', 'w+') as file:
    file.write(json.dumps(worlds) + '\n')
