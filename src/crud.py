import shutil
import src.models as models
import src.schemas as schemas
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


def get_genre_by_name(db: Session, name: str):
    return db.query(models.Genre).filter(models.Genre.name == name).first()


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


def insert_book_genres(db: Session, book_id: int, genres_ids: [int]):
    values = [{'book_id': book_id, 'genre_id': genre_id} for genre_id in genres_ids]
    stmt = models.BookGenre.__table__.insert().prefix_with('IGNORE').values(values)
    db.execute(stmt)
    db.commit()
    return values


def insert_book_writers(db: Session, book_id: int, writers_ids: [int]):
    values = [{'book_id': book_id, 'writer_id': writer_id} for writer_id in writers_ids]
    stmt = models.BookWriter.__table__.insert().prefix_with('IGNORE').values(values)
    db.execute(stmt)
    db.commit()
    return values


def add_book_with_entities(db: Session, db_book: models.Book, writers_str: str, genres_str: str):
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    writers_ids = []
    genres_ids = []
    writers_format_arr = []
    genres_format_arr = []
    writers = writers_str.split(',')
    for writer in writers:
        full_name = writer.split(' ')
        full_name_format = [item.strip().capitalize() for item in full_name]
        writers_format_arr.append(full_name_format)
        writer_from_db = get_writer_by_name(db, full_name_format[0], full_name_format[1])
        if not writer_from_db:
            db_writer = models.Writer(name=full_name_format[0],
                                      lastname=full_name_format[1])
            db.add(db_writer)
            db.commit()
            db.refresh(db_writer)
            writers_ids.append(db_writer.id)
        else:
            writers_ids.append(writer_from_db.id)
    genres = genres_str.split(',')
    for genre in genres:
        genre_format = genre.strip().capitalize()
        genres_format_arr.append(genre_format)
        genre_from_db = get_genre_by_name(db, genre_format)
        if not genre_from_db:
            db_genre = models.Genre(name=genre_format)
            db.add(db_genre)
            db.commit()
            db.refresh(db_genre)
            genres_ids.append(db_genre.id)
        else:
            genres_ids.append(genre_from_db.id)
    book_genres_id_combination = insert_book_genres(db, book_id=db_book.id, genres_ids=genres_ids)
    book_writers_id_combination = insert_book_writers(db, book_id=db_book.id, writers_ids=writers_ids)

    return db_book, writers_format_arr, genres_format_arr
