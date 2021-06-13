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


class Hold(BaseModel):
    username: str 
    password: str
    client_name: str
    request: str
    start_date: str
    start_time: str
    end_time: str
    