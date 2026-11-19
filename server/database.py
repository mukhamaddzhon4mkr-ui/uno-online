from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_engine("sqlite:///uno.db")

class Base(DeclarativeBase):
    pass

def create_tables():
    # создаёт таблицы по моделям, если их нет 
    Base.metadata.create_all(bind=engine)