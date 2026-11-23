from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from server.auth import get_user_by_token
from server.database import engine

class Room:
    def __init__(self, game_id):
        self.game_id = game_id
        self.clients = [] # словарь {"ws": соединение, "name": имя}
        
    async def broadcast(self, message):
        # отправляем всем кто сидит в комнате 
        for client in self.clients:
            await client["ws"].send_json(message)
            
    def names(self):
        result = []
        for client in self.clients:
            result.append(client["name"])
        return result
    
    def remove(self, ws):
        for i in range(len(self.clients)):
            if self.clients[i]["ws"] is ws:
                self.clients.pop(i)
                return
            
rooms = {}

async def handle_room(websocket, game_id, token):
    # Проверка токена до подключения 
    with Session(autoflush=True, bind=engine) as db:
        user = get_user_by_token(db, token)
        if user is None:
            await websocket.close(code=4001)
            return
        username = user.username
        
    await websocket.accept()
    
    if game_id not in rooms:
        rooms[game_id]= Room(game_id)
    room = rooms[game_id]
        
    room.clients.append({"ws": websocket, "name": username})
    await room.broadcast({"type": "room", "players": room.names()}) 
    
    try:
        while True:
            data = await websocket.receive_json()
            await room.broadcast({"type": "echo", "from": username, "data": data})
    except WebSocketDisconnect:
        room.remove(websocket)
        await room.broadcast({"type": "room", "players": room.names()})
           