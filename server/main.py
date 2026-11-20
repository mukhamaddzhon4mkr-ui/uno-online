from fastapi import FastAPI, HTTPException, Cookie, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server.auth import hash_password, check_password, make_token
from server.database import engine, create_tables
from server.models import User, UserSession
from server.schemas import UserIn

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
    
    
#uvicorn server.main:app --reload
