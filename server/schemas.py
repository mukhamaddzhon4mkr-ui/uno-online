from pydantic import BaseModel, Field

class UserIn(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    password: str = Field(min_length=4, max_length=64)