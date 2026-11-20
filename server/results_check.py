import random

from sqlalchemy.orm import Session

from game.game import Game
from game.player import Player

from server.database import engine
from server.models import User, GamePlayer
from server.results import save_game_result

suffix = random.randint(1000, 9999)

with Session(autoflush=True, bind=engine) as db:
    u1 = User(username=f"save_{suffix}_1", password_hash="x")
    u2 = User(username=f"save_{suffix}_2", password_hash="x")
    db.add_all([u1, u2])
    db.commit()
    ids = [u1.id_users, u2.id_users]
    
p1 = Player(ids[0], "Аня")
p2 = Player(ids[1], "Богдан")
game = Game([p1, p2])
game.start_game()

steps = 0
while not game.finished and steps < 200:
    steps += 1
    player = game.current_player()
    
    index = -1
    for i in range(len(player.hand)):
        if player.hand[i].can_play(game.top_card(), game.current_color):
            index = i
            break
    
    if index == -1:
        game.draw_card(player)
        game.pass_turn(player)
    else:
        card = player.hand[index]
        color = None 
        if card.is_wild():
            color = "red"
        game.play_card(player, index, color)

print(f"Партия закончена: {game.finished}, ходов: {steps}")

with Session(autoflush=True, bind=engine) as db:
    game_id = save_game_result(db, "TEST1234", ids[0], game, ids)
    
    print(f"Записана партия id_games = {game_id}")
    print(f"Победитель: {game.winner.name}")
    
    rows = db.query(GamePlayer).filter(GamePlayer.id_games == game_id).all()
    for row in rows:
        print(f"  id_users = {row.id_users} seat = {row.seat} очки = {row.score}, рука = {row.hand}")
        