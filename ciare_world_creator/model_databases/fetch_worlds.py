import asyncio
import copy
import json
import os

import aiohttp
import requests

from ciare_world_creator.utils.style import delete_last_line


def download_world(world_name: str, user: str, path: str):
    headers = {
        "Accept": "application/json, text/plain, */*",
    }

    world_name = world_name.replace(" ", "%20")

    # Get latest version of the world
    url = f"https://fuel.gazebosim.org/1.0/{user}/worlds/{world_name}"
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        version = response.json()["version"]
    else:
        raise RuntimeError(f"Response err {response.status_code} {response.text}")

    # Get all files that this world has
    url = f"https://fuel.gazebosim.org/1.0/{user}/worlds/{world_name}/{version}/files"
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        files = response.json()["file_tree"]

    else:
        raise RuntimeError(f"Response err {response.status_code} {response.text}")

    sdf_file = None
    for file in files:
        # TODO use regex
        if ".sdf" in file["name"]:
            sdf_file = file["path"]
    if not sdf_file:
        return None

    url = f"https://fuel.gazebosim.org/1.0/{user}/worlds/{world_name}/{version}/files{sdf_file}"

    if sdf_file[0] == "/":
        sdf_file = sdf_file[1:]
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(os.path.join(path, sdf_file), "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print("File downloaded successfully.")
        return os.path.join(path, sdf_file)
    else:
        print(
            f"Response err {response.status_code} {response.text} in downloading world https://fuel.gazebosim.org/1.0/{user}/worlds/{world_name}/{version}/files{sdf_file}"
        )


async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
        try:
            response_data = await response.json()
            return response_data
        except aiohttp.client_exceptions.ContentTypeError:
            return {"message": "Page not found"}


async def fetch_worlds(fp: str):
    url = "https://fuel.gazebosim.org/1.0/worlds"
    params = {"page": 1}
    worlds = []

    should_stop = False
    async with aiohttp.ClientSession() as session:
        while not should_stop:
            if params["page"] != 1:
                delete_last_line()
            print(f"Fetching worlds page {params['page']}")
            tasks = []
            batch_size = 5  # Number of requests to send in parallel

            for _ in range(batch_size):
                tasks.append(fetch(session, url, copy.deepcopy(params)))
                # print(params)
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

    print(f"Saved worlds at {fp}")


if __name__ == "__main__":
    asyncio.run(fetch_worlds())
