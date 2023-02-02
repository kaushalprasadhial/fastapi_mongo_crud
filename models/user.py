from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    password: str
    
class Base(BaseModel):
    name: str
    email: str
    password: str
    image: Optional[str] = None