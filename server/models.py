from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from server.database import Base

class User(Base):
    __tablename__ = "users"
    
    id_users = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, nullable = False, unique = True)
    password_hash = Column(Text, nullable = False)
    created_at = Column(DateTime, default = datetime.now)
    
class UserSession(Base):
    __tablename__ = "sessions"
    
    id_sessions = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Text,  nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    
    id_users = Column(Integer, ForeignKey("users.id_users"), nullable=False)
    user = relationship("User")
    
class Game(Base):
    __tablename__ = "games"
    
    id_games = Column(Integer, primary_key=True, autoincrement=True)
    room_code = Column(Text, nullable=False)
    status = Column(Text, default="waiting") # waiting, playing, finished
    created_at = Column(DateTime, default = datetime.now)
    
    id_users_host = Column(Integer, ForeignKey("users.id_users"))
    id_users_winner = Column(Integer, ForeignKey("users.id_users"), nullable=True)
    
    players = relationship("GamePlayer", back_populates="game")
    
class GamePlayer(Base):
    __tablename__ = "game_players"
    id_game_players = Column(Integer, primary_key=True, autoincrement=True)
    seat = Column(Integer, default=0)
    hand = Column(Text, default="[]") # карты игрока в Json
    score = Column(Integer, default=0)
    
    id_games = Column(Integer, ForeignKey("games.id_games"))
    id_users = Column(Integer, ForeignKey("users.id_users"))
    
    game = relationship("Game", back_populates="players")
    user = relationship("User")
    
class Move(Base):
    __tablename__ = "moves"
    
    id_moves = Column(Integer, primary_key=True, autoincrement=True)
    card = Column(Text)
    action = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    id_games = Column(Integer, ForeignKey("games.id_games"))
    id_game_players = Column(Integer, ForeignKey("game_players.id_game_players"))
    
    game = relationship("Game")
    
if __name__ == "__main__":
    from sqlalchemy import inspect
    from server.database import create_tables, engine
    
    create_tables()
    print("Таблицы:", inspect(engine).get_table_names())