import asyncio
import aiohttp
import json

async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
            print(params)
            try:
                response_data = await response.json()
                return response_data
            except aiohttp.client_exceptions.ContentTypeError:
                print("Response with 'Page not found' received.")
                return {'message': 'Page not found'}
            
async def main():
    url = 'https://fuel.gazebosim.org/1.0/models'
    params = {'page': 1}
    worlds = []

    should_stop = False
    async with aiohttp.ClientSession() as session:
        while not should_stop:
            tasks = []
            batch_size = 5  # Number of requests to send in parallel

            for _ in range(batch_size):
                tasks.append(fetch(session, url, params))
                params['page'] += 1

            # Execute the requests in parallel
            responses = await asyncio.gather(*tasks)

            for response_data in responses:
                if isinstance(response_data, dict) and response_data.get('message') == 'Page not found':
                    print("Response with 'Page not found' received.")
                    should_stop = True
                    break
                
                worlds.extend(response_data)

            if len(responses) < batch_size:
                # Break the loop if fewer responses were received than expected
                break

    with open('output_models.json', 'w+') as file:
        file.write(json.dumps(worlds) + '\n')

if __name__ == '__main__':
    asyncio.run(main())