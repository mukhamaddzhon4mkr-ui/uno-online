import json 

from server.models import Game, GamePlayer


def save_game_result(db, room_code, host_id, game, user_ids):
    if not game.finished:
        return None
    
    winner_id = None
    if game.winner is not None:
        index = game.players.index(game.winner)
        winner_id = user_ids[index]
        
    db_game = Game(room_code=room_code, status="finished", id_users_host=host_id, id_users_winner=winner_id)
    db.add(db_game)
    db.commit()
    
    for i in range(len(game.players)):
        players = game.players[i]
        
        hand = []
        for card in players.hand:
            hand.append(card.to_dict())
            
        row = GamePlayer(id_games=db_game.id_games, id_users=user_ids[i], seat=i, hand=json.dumps(hand, ensure_ascii=False), score=players.hand_points())
        db.add(row)
        
    db.commit()
    return db_game.id_games
