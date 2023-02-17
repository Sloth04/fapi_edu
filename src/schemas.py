import datetime
from enum import Enum
from typing import Optional, Union, List
from pydantic import BaseModel, EmailStr, Field

password_regex = "[A-Za-z0-9@#$%^&+_=]{8,}"


class EmailSchema(BaseModel):
    email: List[EmailStr]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Tags(Enum):
    books = "books"
    writers = "writers"
    users = "users"


class Role(str, Enum):
    admin = 'admin'
    user = 'user'


class PaginationQueryParams:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., regex=password_regex)
    role: Role = Role.user


class UserUpdate(UserBase):
    password: str


class User(UserBase):
    id: int
    role: Role = Role.user
    disable: bool = False
    qr_code_link: Optional[str] = None

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    title: str
    writer_id: str
    description: Union[str, None] = None
    publish_date: datetime.date
    rating: int
    genres: str

    class Config:
        schema_extra = {
            "example": {
                "title": "Book",
                "writer_id": 1,
                "description": "Pretty Book",
                "publish_date": datetime.date.today(),
                "rating": 10,
                "genres": "genre"
            }
        }


class BookCreate(BookBase):
    cover_file: str
    book_file: str


class Book(BookBase):
    id: int
    cover_file: str
    book_file: str

    class Config:
        orm_mode = True


class WriterBase(BaseModel):
    name: str
    lastname: str
    born: datetime.date
    died: Union[datetime.date, None] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Fred",
                "lastname": "The Writer",
                "born": datetime.date.today(),
                "died": None,
            }
        }


class WriterCreate(WriterBase):
    pass


class Writer(WriterBase):
    id: int

    class Config:
        orm_mode = True
