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
    print(f"Downloading model files for model {model} and saving to {directory}")
    parent_dir = os.path.basename(directory) 
    if parent_dir != model:
        directory = os.path.join(directory, model)
        
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
        download_model(username, model, path, directory)

def download_model(username, model, file_path, directory):
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


# Usage example
username = 'chapulina'
model = 'Apartment'
version = '1'
download_model_files(username, model, version, directory='/var/tmp/ciare/models')
