import shutil
import models
import schemas
import re
from sqlalchemy.orm import Session
from fastapi import UploadFile


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
    with open(f'{file.filename}', "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
