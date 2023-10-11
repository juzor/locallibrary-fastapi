from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Role(BaseModel):
    id: int
    name: str
    default: bool 
    permissions: int

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    active: bool
    role: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str