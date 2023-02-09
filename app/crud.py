import shutil
import app.models as models
import app.schemas as schemas
import pyotp
from sqlalchemy.orm import Session
from fastapi import UploadFile
from security import pwd_context


def get_writers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Writer).offset(skip).limit(limit).all()


def get_writer_by_id(db: Session, writer_id: int):
    return db.query(models.Writer).filter(models.Writer.id == writer_id).first()


def delete_writer_by_id(db: Session, writer: models.Writer):
    db.delete(writer)
    db.commit()
    return True


def get_writer_by_name(db: Session, name: str, lastname: str):
    return db.query(models.Writer).filter(models.Writer.name == name, models.Writer.lastname == lastname).first()


def get_books(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_book_by_id(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def delete_book_by_id(db: Session, book: models.Book):
    db.delete(book)
    db.commit()
    return True


def get_book_by_title(db: Session, title: str):
    return db.query(models.Book).filter(models.Book.title == title).first()


def add_writer(db: Session, writer: schemas.WriterCreate):
    db_writer = models.Writer(**writer.dict())
    db.add(db_writer)
    db.commit()
    db.refresh(db_writer)
    return db_writer


def add_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def save_file(file: UploadFile):
    with open(f'{file.filename}', "w+b") as buffer:
        shutil.copyfileobj(file.file, buffer)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        otp_secret=pyotp.random_base32(),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_self(db: Session, current_user: schemas.User, user_update: schemas.UserUpdate):
    db_user = get_user(db, current_user.id)
    db_user.email = user_update.email
    db_user.username = user_update.username
    db_user.full_name = user_update.full_name
    db_user.hashed_password = pwd_context.hash(user_update.password)
    db.commit()
    db.refresh(db_user)
    return db_user
