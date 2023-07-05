import asyncio
import copy
import json

import aiohttp

from ciare_world_creator.utils.style import delete_last_line


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
