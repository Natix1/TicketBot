import aiohttp

global http_session
http_session: aiohttp.ClientSession | None = None

def get_session() -> aiohttp.ClientSession:
    global http_session

    if http_session is None or http_session.closed:
        http_session = aiohttp.ClientSession()

    return http_session

async def close_session() -> None:
    if http_session and not http_session.closed:
        await http_session.close()

async def get(url: str, headers: dict | None) -> dict:
    session = get_session()
    async with session.get(url=url, headers=headers) as resp:
        if resp.status != 200:
            raise Exception(f"Failed GET request to {url}. Status code: {resp.status}")
        
        data = await resp.json()
        return data
    
async def post(url: str, json: dict | None, headers: dict | None) -> dict:
    session = get_session()
    async with session.post(url=url, json=json, headers=headers) as resp:
        if resp.status != 200:
            raise Exception(f"Failed POST request to {url}. Status code: {resp.status}")
        
        data = await resp.json()
        return data