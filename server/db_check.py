from sqlalchemy.orm import Session

from server.database import engine
from server.models import User, Game, GamePlayer, Move

with Session(autoflush=True, bind=engine) as db:
    old = db.query(User).filter(User.username == "test_player").first()
    if old is not None:
        db.delete(old)
        db.commit()
        
    # первый пользователь
    user = User(username="test_player", password_hash="12345")
    db.add(user)
    db.commit()
    print(f"Пользователь: id={user.id_users}, имя={user.username}")
        
    # Партия в его комнате
    game = Game(room_code="ABCD", id_users_host=user.id_users, status="finished")
    db.add(game)
    db.commit()
    print(f"Партия: id={game.id_games}, код={game.room_code}")
    
    #Участие в партии
    player = GamePlayer(id_games=game.id_games, id_users=user.id_users, seat=1, score=40)
    db.add(player)
    db.commit()
    print(f"Участник: id={player.id_game_players}, очки={player.score}")
    
    #Ход в партии
    move = Move(id_games=game.id_games, id_game_players=player.id_game_players, card="red 7", action="play")
    db.add(move)
    db.commit()
    print(f"Ход: id={move.id_moves}, карта={move.card}")

    # проверяем обратные связи
    print(f"Участников в партии: {len(game.players)}")
    print(f"Хозяин партии: {game.id_users_host}")
    print(f"Игрок участника: {player.user.username}")