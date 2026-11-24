import requests

BASE_URL = "http://127.0.0.1:8000"

# сессия помнит cookie с токеном входа
SESSION = requests.Session()


def _read(response):
    # разбираем ответ сервера в одном месте
    if response.status_code == 200:
        return response.json(), None

    try:
        detail = response.json().get("detail", "Ошибка сервера")
    except ValueError:
        detail = "Ошибка сервера"
    return None, detail


def register(username, password):
    try:
        response = SESSION.post(f"{BASE_URL}/register", json={"username": username, "password": password}, timeout=5)
    except requests.exceptions.RequestException:
        return None, "Сервер не отвечает"
    return _read(response)


def login(username, password):
    try:
        response = SESSION.post(f"{BASE_URL}/login", json={"username": username, "password": password}, timeout=5)
    except requests.exceptions.RequestException:
        return None, "Сервер не отвечает"
    return _read(response)


def logout():
    try:
        response = SESSION.post(f"{BASE_URL}/logout", timeout=5)
    except requests.exceptions.RequestException:
        return None, "Сервер не отвечает"
    return _read(response)


def list_games():
    try:
        response = SESSION.get(f"{BASE_URL}/games", timeout=5)
    except requests.exceptions.RequestException:
        return None, "Сервер не отвечает"
    return _read(response)


def create_game():
    try:
        response = SESSION.post(f"{BASE_URL}/games", timeout=5)
    except requests.exceptions.RequestException:
        return None, "Сервер не отвечает"
    return _read(response)