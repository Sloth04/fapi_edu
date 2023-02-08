import os
import crud
import models
import schemas
import datetime
import pathlib
from database import SessionLocal
from typing import Union, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter, Form, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse

library_router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


cwd = pathlib.Path().cwd()


@library_router.get("/writer/{writer_id}/info", response_model=schemas.Writer, tags=[schemas.Tags.writers],
                    summary="Get writer")
def get_writer(writer_id: int, db: Session = Depends(get_db)):
    writer = crud.get_writer_by_id(db, writer_id=writer_id)
    if writer is None:
        raise HTTPException(status_code=404, detail="Writer not found")
    return writer


@library_router.post("/writer/add", response_model=schemas.Writer, tags=[schemas.Tags.writers], summary="Add writer")
def add_writer(writer: schemas.WriterCreate, db: Session = Depends(get_db)):
    is_writer_reg = crud.get_writer_by_name(db, name=writer.name, lastname=writer.lastname)
    if is_writer_reg:
        raise HTTPException(status_code=400, detail="Writer already added")
    return crud.add_writer(db=db, writer=writer)


@library_router.get("/book/{book_id}/info", response_model=schemas.Book, tags=[schemas.Tags.books])
def get_book_info(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    else:
        return book


@library_router.get("/book/{book_id}/download", response_model=schemas.Book, tags=[schemas.Tags.books])
def download_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    file = pathlib.Path(book.book_file)
    if file.exists():
        return FileResponse(file, filename=file.name)
    else:
        raise HTTPException(status_code=404, detail="Book file not found")


@library_router.get("/books/", response_model=List[schemas.Book], tags=[schemas.Tags.books])
def get_books(params: schemas.PaginationQueryParams = Depends(),
              db: Session = Depends(get_db)):
    items = crud.get_books(db, skip=params.skip, limit=params.limit)
    return items


@library_router.get("/writers/", response_model=List[schemas.Writer], tags=[schemas.Tags.writers])
def get_writers(params: schemas.PaginationQueryParams = Depends(),
                db: Session = Depends(get_db)):
    items = crud.get_writers(db, skip=params.skip, limit=params.limit)
    return items


@library_router.post("/book/add_info", response_model=schemas.Book, tags=[schemas.Tags.books])
def add_book_info(book: schemas.BookCreate, db: Session = Depends(get_db)):
    is_book_reg = crud.get_book_by_title(db, title=book.title)
    if is_book_reg:
        raise HTTPException(status_code=400, detail="Book already added")
    return crud.add_book(db=db, book=book)


@library_router.post("/book/add_form", response_model=schemas.Book, tags=[schemas.Tags.books])
def add_book_form(background_tasks: BackgroundTasks,
                  title: str = Form(...),
                  writer_id: Optional[int] = Form(default=None),
                  description: Optional[str] = Form(default=None),
                  publish_date: datetime.date = Form(default=datetime.date.today()),
                  rating: Optional[int] = Form(default=None),
                  cover_filename: Optional[str] = Form(default=None),
                  book_filename: Optional[str] = Form(default=None),
                  genres: Optional[str] = Form(default=None),
                  cover_file: Optional[UploadFile] = File(default=None),
                  book_file: UploadFile = File(...),
                  db: Session = Depends(get_db)):
    if cover_filename is None:
        cover_filename = cwd / "media" / "covers" / f"{cover_file.filename}"
        cover_file.filename = cover_filename
    else:
        cover_file.filename = cwd / "media" / "covers" / f"{cover_filename}{pathlib.Path(cover_file.filename).suffix}"

    if book_filename is None:
        book_filename = cwd / "media" / "books" / f"{book_file.filename}"
        book_file.filename = book_filename
    else:
        book_file.filename = cwd / "media" / "books" / f"{book_filename}{pathlib.Path(book_file.filename).suffix}"

    if cover_file.content_type == 'image/png' or cover_file.content_type == 'image/jpeg':
        background_tasks.add_task(crud.save_file, cover_file)
    else:
        raise HTTPException(status_code=418, detail="Unsupported format, must be .jpg or .png")

    if book_file.content_type == 'application/epub+zip' or book_file.content_type == 'text/plain':
        book_file.filename = cwd / "media" / "books" / f"{book_file.filename}"
        background_tasks.add_task(crud.save_file, book_file)
    else:
        raise HTTPException(status_code=418, detail="Unsupported format, must be .epub or .txt")

    is_book_reg = crud.get_book_by_title(db, title=title)
    if is_book_reg:
        raise HTTPException(status_code=400, detail="Book already added")
    db_book = models.Book(title=title,
                          writer_id=writer_id,
                          description=description,
                          publish_date=publish_date,
                          rating=rating,
                          cover_file=cover_file.filename,
                          book_file=book_file.filename,
                          genres=genres)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@library_router.delete("/book/{book_id}", tags=[schemas.Tags.books])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    deleted = crud.delete_book_by_id(db, book)
    if deleted:
        return {"deleted_book": book}
    else:
        raise HTTPException(status_code=404, detail="Unexpected error")


@library_router.delete("/writer/{writer_id}", tags=[schemas.Tags.writers])
def delete_writer(writer_id: int, db: Session = Depends(get_db)):
    writer = crud.get_writer_by_id(db, writer_id=writer_id)
    if writer is None:
        raise HTTPException(status_code=404, detail="Book not found")
    deleted = crud.delete_book_by_id(db, writer)
    if deleted:
        return {"deleted_writer": writer}
    else:
        raise HTTPException(status_code=404, detail="Unexpected error")
