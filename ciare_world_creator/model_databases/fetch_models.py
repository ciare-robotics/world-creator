import asyncio
import copy
import json

import aiohttp

from ciare_world_creator.utils.style import delete_last_line
import os
import requests
from pprint import pprint

def retrieve_paths(json_data, parent_path=''):
    paths = []
    file_tree = json_data
    
    if isinstance(file_tree, dict):
        file_tree = file_tree.get('file_tree', [])
    
    for item in file_tree:
        current_path = item['path']
        if 'name' in item:  # Check if it represents a file
            paths.append(current_path)
        
        if 'children' in item:
            children = item['children']
            
            if isinstance(children, list):
                children_paths = retrieve_paths(children, current_path)
                paths.extend(children_paths)
            elif isinstance(children, dict):
                child_paths = retrieve_paths([children], current_path)
                paths.extend(child_paths)
    
    return paths

def download_model_files(username, model, version, directory=''):
    parent_dir = os.path.basename(directory) 
    if parent_dir != model:
        directory = os.path.join(directory, model)
    if os.path.exists(directory):
        print("Model {model} already exists at {directory}, not downloaiding it")
        return 
    print(f"Downloading model files for model {model} and saving to {directory}")
    # Create a directory with the model name if no custom directory is provided
    if not directory:
        directory = model
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Get the file tree
    url = f"https://fuel.gazebosim.org/1.0/{username}/models/{model}/{version}/files"
    response = requests.get(url)
    file_tree = response.json()
    
    # Download each file or recursively process directories
    paths = retrieve_paths(file_tree)

    for path in paths:
        if len(path.split(".")) == 1:
            continue
        download_model(username, model, version, path, directory)

def download_model(username, model, version, file_path, directory):
    gz_server_file_path = file_path[1:] if file_path[0] == "/" else file_path
    local_file_path = os.path.join(directory, gz_server_file_path)

    
    if not os.path.exists(os.path.dirname(local_file_path)):
        os.makedirs(os.path.dirname(local_file_path))

    file_name = os.path.basename(file_path)
    download_url = f"https://fuel.gazebosim.org/1.0/{username}/models/{model}/{version}/files/{gz_server_file_path}"
    response = requests.get(download_url)
    if response.status_code == 200:
        # file_path = os.path.join(directory, file_name)
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download: {file_name}")



async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
        try:
            response_data = await response.json()
            return response_data
        except aiohttp.client_exceptions.ContentTypeError:
            return {"message": "Page not found"}


async def fetch_models(fp: str):
    url = "https://fuel.gazebosim.org/1.0/models"
    params = {"page": 1}
    worlds = []

    should_stop = False

    async with aiohttp.ClientSession() as session:
        while not should_stop:
            if params["page"] != 1:
                delete_last_line()
            print(f"Fetching models page {params['page']}")
            tasks = []
            batch_size = 5  # Number of requests to send in parallel

            for _ in range(batch_size):
                tasks.append(fetch(session, url, copy.deepcopy(params)))

                params["page"] += 1
            # Execute the requests in parallel
            responses = await asyncio.gather(*tasks)

            for response_data in responses:
                if (
                    isinstance(response_data, dict)
                    and response_data.get("message") == "Page not found"
                ):
                    should_stop = True
                    break

                worlds.extend(response_data)

            if len(responses) < batch_size:
                # Break the loop if fewer responses were received than expected
                break

    with open(fp, "w+") as file:
        file.write(json.dumps(worlds) + "\n")
    print(f"Saved models at {fp}")


if __name__ == "__main__":
    asyncio.run(fetch_models())
