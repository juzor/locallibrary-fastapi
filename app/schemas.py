from typing import Optional, List
from datetime import datetime
from pydantic import UUID4, BaseModel, EmailStr
from app import models

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

class BookBase(BaseModel):
    title: str
    author: str

class BookOut(BookBase):
    id: int

class BookInstanceOut(BaseModel):
    id: Optional[UUID4] = None
    book_id: Optional[int] = None
    imprint: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[models.StatusEnum] = None
    user_id: Optional[int]

class BookDetailOut(BookOut):
    summary: str
    isbn: str
    img_url: Optional[str]
    language: Optional[str] = None
    book_instances: List[BookInstanceOut]

class AuthorBase(BaseModel):
    name: str
    date_of_birth: Optional[datetime] = None
    date_of_death: Optional[datetime] = None

class AuthorOut(AuthorBase):
    id: int

class AuthorDetailOut(AuthorOut):
    books: List[BookOut]

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(AuthorBase):
    pass

class BookCreate(BaseModel):
    title: str
    summary: str
    isbn: str
    img_url: Optional[str] = None
    language_id: Optional[int] = None
    author_id: Optional[int] = None
    copies: int
    imprint: Optional[str] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    isbn: Optional[str] = None
    img_url: Optional[str] = None

class GenreBase(BaseModel):
    name: str

class GenreOut(GenreBase):
    id: int

class GenreCreate(GenreBase):
    pass

class GenreDetailOut(GenreOut):
    books: Optional[List[BookOut]]