from typing import Optional
from pydantic import BaseModel

class Item(BaseModel):
    client: str
    request: str
    create_date: str
    start_date:str
    res_start: str
    res_end: str    
    facility: Optional[str] = "Team 3 Chicago"

class Client(BaseModel):
    name: str
    password: str
    status: str
    balance: float
    role: str

class Login(BaseModel):
    username: str
    password: str
    