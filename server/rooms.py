import random 

from server.models import Game

CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def make_room_code():
    code = "".join(random.choices(CHARS, k=8))
    return code

def make_unique_code(db):
    while True:
        code = make_room_code()
        game = db.query(Game).filter(Game.room_code == code).first()
        if game is None:
            return code
        