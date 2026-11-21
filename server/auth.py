import hashlib
import secrets

from server.models import User, UserSession

def hash_password(password):
    salt = secrets.token_hex(8)
    digest = hashlib.sha256((salt+password).encode("utf-8")).hexdigest()
    return salt + "$" + digest


def check_password(password, stored):
    parts = stored.split("$")
    if len(parts) !=2:
        return False
    salt = parts[0]
    digest = parts[1]
    test = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return test == digest

def make_token():
    return secrets.token_hex(16)

def get_user_by_token(db, token):
    session = db.query(UserSession).filter(UserSession.token == token).first()
    if session is None:
        return None
    return db.get(User, session.id_users)