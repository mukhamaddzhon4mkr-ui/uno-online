from fastapi import FastAPI

app = FastAPI(title = "UNO Online")


@app.get("/")
def index():
    return {"status": "ok", "message": "Сервер UNO работает"}

#uvicorn server.main:app --reload