from helpers.async_requests import post

async def paste(content: str) -> str:
    # {"files":[{"content":"asgagas412r121g1gf12g1"}]}
    # https://sourceb.in/api/bins

    resp = await post(
        url="https://sourceb.in/api/bins",
        json={
            "files": [ { "content": content }]
        },
        headers={
            "Content-Type": "application/json"
        }
    )

    if resp:
        key = resp.get("key")
        if not key:
            raise Exception("Got malformed response from sourcebin")
        
        return f"https://sourceb.in/{key}"
    
    raise Exception("Failed POST request to sourcebin.")