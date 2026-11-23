import asyncio
import json
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

async def read(ws, name, timeout=3):
    try:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        print(f"{name}: {raw[:160]}")
        return json.loads(raw)
    except asyncio.TimeoutError:
        print(f"{name}: тишина")
        return None
        

# async def listen(name, game_id, token, seconds=3):
#     uri = f"ws://127.0.0.1:8000/ws/game/{game_id}?token={token}"
#     async with websockets.connect(uri) as ws:
#         start = asyncio.get_event_loop().time()
#         while asyncio.get_event_loop().time() - start < seconds:
#             try:
#                 message = await asyncio.wait_for(ws.recv(), timeout=1)
#                 print(f"{name}: {message}")
#             except asyncio.TimeoutError:
#                 pass
       
async def main():
    name1, token1, session = make_user("ws_a")
    name2, token2, session2 = make_user("ws_b")
    
    game = session.post(f"{BASE}/games").json()
    game_id = game["id_games"]
    print("игра:", game)
    
    url1 = f"ws://127.0.0.1:8000/ws/game/{game_id}?token={token1}"
    url2 = f"ws://127.0.0.1:8000/ws/game/{game_id}?token={token2}"
    
    ws1 = await websockets.connect(url1)
    await read(ws1, "A")
    ws2 = await websockets.connect(url2)
    await read(ws1, "A")
    await read(ws2, "B")
    
    await ws1.send(json.dumps({"type": "start"}))
    state_a = await read(ws1, "A")
    await read(ws2, "B")
    if state_a is not None:
        print("карта у A:", len(state_a.get("hand", [])))
        
    await ws1.send(json.dumps({"type": "play", "index": 0}))
    await read(ws1,"A")
    await read(ws2,"B")
    
    await ws1.close()
    await ws2.close()
    
asyncio.run(main())