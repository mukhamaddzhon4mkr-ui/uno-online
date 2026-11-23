import asyncio
import random

import requests
import websockets

BASE = "http://127.0.0.1:8000"


def make_user(prefix):
    name = prefix + str(random.randint(1000, 9999))
    requests.post(f"{BASE}/register", json={"username": name, "password": "1234"})
    
    session = requests.Session()
    session.post(f"{BASE}/login", json={"username": name, "password": "1234"})
    token = session.cookies.get("session_token")
    return name, token, session

async def listen(name, game_id, token, seconds=3):
    uri = f"ws://127.0.0.1:8000/ws/game/{game_id}?token={token}"
    async with websockets.connect(uri) as ws:
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < seconds:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=1)
                print(f"{name}: {message}")
            except asyncio.TimeoutError:
                pass
            
async def main():
    name1, token1, session = make_user("ws_a")
    name2, token2, session2 = make_user("ws_b")
    
    game = session.post(f"{BASE}/games").json()
    game_id = game["id_games"]
    print("игра:", game)
    
    await asyncio.gather(
        listen(name1, game_id, token1),
        listen(name2, game_id, token2),
    )
    
asyncio.run(main())