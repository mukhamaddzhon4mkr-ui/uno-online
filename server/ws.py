import json

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from game.game import Game
from game.player import Player
from server.auth import get_user_by_token
from server.database import engine
from server.models import Game as DbGame


class Room:
    def __init__(self, game_id, room_code):
        self.game_id = game_id
        self.room_code = room_code
        self.clients = [] # {"ws": соединение, "name": имя}
        self.game = None

        
        
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
    
    async def send_error(self, client, text):
        await client["ws"].send_json({"type": "error", "message": text, })
    
    def player_by_name(self, name):
        if self.game is None:
            return None
        for player in self.game.players:
            if player.name == name:
                return player
            return player
        return None
    
    async def send_state(self):
        # Каждому отправляем общий стол и только его руку
        for client in self.clients:
            player = self.player_by_name(client["name"])
            hand = []
            if player is not None:
                hand = self.game.hand_list(player)
            
            await client["ws"].send_json({
                "type": "state",
                "state": self.game.state_dict(),
                "hand": hand,
            })
            
    async def start(self, client):
        if web_is_host(self, client) is False:
            await self.send_error(client, "Начать партию может хозяин комнаты")
            return
        if len(self.clients) < 2:
            await self.send_error(client, "Нужно хотя бы двое игроков")
            return
        
        players = []
        for c in self.clients:
            players.append(Player(c["user_id"], c["name"]))
            
        self.game = Game(players)
        self.game.start_game()
        await self.send_state()
        
    async def play(self, client, data):
        player = self.player_by_name(client["name"])
        if self.game is None or player is None:
            await self.send_error(client, "Партия ещё не началась")
            return
        
        error = self.game.play_card(player, data.get("index", -1), data.get("color"))
        if error is not None:
            await self.send_error(client, error)
        else:
            await self.send_state()
            
    async def draw(self, client):
        player = self.player_by_name(client["name"])
        if self.game is None or player is None:
            await self.send_error(client, "Партия ещё не началась")
            return
        
        error = self.game.draw_card(player)
        if error is not None:
            await self.send_error(client, error)
        else:
            await self.send_state()
    
    async def pass_turn(self, client):
        player = self.player_by_name(client["name"])
        if self.game is None or player is None:
            await self.send_error(client, "Партия ещё не началась")
            return
        
        error = self.game.pass_turn(player)
        if error is not None:
            await self.send_error(client, error)
        else:
            await self.send_state()
    
    async def say_uno(self, client):
        player = self.player_by_name(client["name"])
        if self.game is None or player is None:
            await self.send_error(client, "Партия ещё не началась")
            return
        
        self.game.say_uno(player)
        await self.send_state()
        

def web_is_host(room, client):
    # Хозяиин тот кто первый поключился
    if len(room.clients) == 0:
        return False
    return room.clients[0]["ws"] is client["ws"]

                
            
rooms = {}

async def handle_room(websocket, game_id, token):
    # Проверка токена до подключения 
    with Session(autoflush=True, bind=engine) as db:
        user = get_user_by_token(db, token)
        if user is None:
            await websocket.close(code=4001)
            return
        
        username = user.username
        user_id = user.id_users
        
        db_game = db.get(DbGame, game_id)
        if db_game is None:
            await websocket.close(code=4004)
            return
        room_code = db_game.room_code    
        
    await websocket.accept()
    
    if game_id not in rooms:
        rooms[game_id] = Room(game_id, room_code)
    room = rooms[game_id]
    
    client = ({"ws": websocket, "user_id": user_id, "name": username})
    room.clients.append(client)
    
    await room.broadcast({"type": "room", "room_code": room_code, "players": room.names()}) 
    
    
    try:
        while True:
            data = await websocket.receive_json()
            kind = data.get("type")
            
            if kind == "start":
                await room.start(client)
            elif kind == "play":
                await room.play(client, data)
            elif kind == "draw":
                await room.draw(client)
            elif kind == "pass":
                await room.pass_turn(client)
            elif kind == "uno":
                await room.uno(client)
            else:
                await room.send_error(client, "Неизвестная команда")
    except WebSocketDisconnect:
        room.remove(websocket)
        await room.broadcast({"type": "room", "players": room.names()})
           