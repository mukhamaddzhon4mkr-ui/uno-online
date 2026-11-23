from fastapi import FastAPI, HTTPException, Cookie, Response, WebSocket
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server.auth import hash_password, check_password, make_token, get_user_by_token
from server.database import engine, create_tables
from server.models import User, UserSession, Game, GamePlayer
from server.rooms import make_unique_code
from server.schemas import UserIn
from server.ws import handle_room


app = FastAPI(title = "UNO Online")

create_tables()

@app.get("/")
def index():
    return {"status": "ok", "message": "Сервер UNO работает"}

@app.post("/register")
def register(data: UserIn):
    with Session(autoflush=True, bind=engine) as db:
        old = db.query(User).filter(User.username == data.username).first()
        if old is not None:
            raise HTTPException(status_code=400, detail="Такой логин уже занят")
        
        user = User(username=data.username, password_hash=hash_password(data.password))
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Такой логин уже занят")
        
        return {"id_users": user.id_users, "username": user.username}
    

@app.post("/login")
def login(data: UserIn, response: Response):
    with Session(autoflush=True, bind=engine) as db:
        user = db.query(User).filter(User.username == data.username).first()
        if user is None or not check_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        
        token = make_token()
        username = user.username
        session = UserSession(token=token, id_users=user.id_users)
        db.add(session)
        db.commit()
        
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=3600, samesite="lax")
    return {"status": "ok", "username": username}

@app.get("/me")
def me(session_token: str | None = Cookie(default=None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail="Ты не вошёл")
    
    with Session(autoflush=True, bind=engine) as db:
        session = db.query(UserSession).filter(UserSession.token == session_token).first()
        if session is None:
            raise HTTPException(status_code=401, detail="Сессия не найдена")
        
        user = db.get(User, session.id_users)
        return {"id_users": user.id_users, "username": user.username}

@app.post("/logout")
def logout(response: Response, session_token: str | None = Cookie(default=None)):
    if session_token is not None:
        with Session(autoflush=True, bind=engine) as db:
            session = db.query(UserSession).filter(UserSession.token == session_token).first()
            if session is not None:
                db.delete(session)
                db.commit()
    
    response.delete_cookie("session_token")
    return {"status": "ok"}
    
@app.post("/games")
def create_game(session_token: str | None = Cookie(default=None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail="Ты не вошёл")
    
    with Session(autoflush=True, bind=engine) as db:
        user = get_user_by_token(db, session_token)
        if user is None:
            raise HTTPException(status_code=401, detail="Сесcия не найдена")
        
        code = make_unique_code(db)
        game = Game(room_code=code, status="waiting", id_users_host=user.id_users)
        db.add(game)
        db.commit()
        
        player = GamePlayer(id_games=game.id_games, id_users=user.id_users, seat=0)
        db.add(player)
        db.commit()
        
        return {"id_games": game.id_games, "room_code": code, "status": "waiting"}
    
@app.get("/games")
def list_games():
    with Session(autoflush=True, bind=engine) as db:
        games = db.query(Game).filter(Game.status == "waiting").all()
        
        result = []
        for game in games:
            host = db.get(User, game.id_users_host)
            players = db.query(GamePlayer).filter(GamePlayer.id_games == game.id_games).all()
            
            result.append({
                "id_games": game.id_games,
                "room_code": game.room_code,
                "host": host.username,
                "players": len(players),
                "status": game.status,
            })
    return result
    

@app.websocket("/ws/game/{game_id}")
async def game_socket(websocket: WebSocket, game_id: int, token: str):
    await handle_room(websocket, game_id, token)
#uvicorn server.main:app --reload
