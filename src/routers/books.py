import datetime
import pathlib
from typing import Optional, List

from fastapi import HTTPException, Depends, APIRouter, Form, UploadFile, File, Request
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse

import src.crud as crud
import src.dependencies as dependencies
import src.models as models
import src.schemas as schemas
from settings import *
from src.internal.roles import allow_create_and_delete_resource

books_router = APIRouter()


@books_router.get("/book/{book_id}/info", response_model=schemas.Book, tags=[schemas.Tags.books])
async def get_book_info(book_id: int, db: Session = Depends(dependencies.get_db)):
    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    else:
        return book


@books_router.get("/book/{book_id}/download", response_model=schemas.Book, tags=[schemas.Tags.books])
async def download_book_by_id(book_id: int, db: Session = Depends(dependencies.get_db)):
    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    file = cwd / 'media' / pathlib.Path(book.book_file)
    if file.exists():
        return FileResponse(file, filename=file.name)
    else:
        raise HTTPException(status_code=404, detail="Book file not found")


@books_router.get("/books/", response_model=List[schemas.Book], tags=[schemas.Tags.books])
async def get_books(request: Request,
                    params: schemas.PaginationQueryParams = Depends(),
                    db: Session = Depends(dependencies.get_db)):
    books = []
    items = crud.get_books(db, skip=params.skip, limit=params.limit)
    for item in items:
        book = schemas.Book(**item[0].__dict__)
        book.writer = [item[1]]
        book.genres = [item[2]]
        img_url = request.url_for('media', path=book.cover_file.replace('\\', '/'))
        book_url = request.url_for('media', path=book.book_file.replace('\\', '/'))
        book.cover_file = img_url
        book.book_file = book_url
        books.append(book)
    return books


@books_router.post("/book/add_info", response_model=schemas.Book, tags=[schemas.Tags.books])
async def add_book_info(book: schemas.BookCreate, db: Session = Depends(dependencies.get_db)):
    is_book_reg = crud.get_book_by_title(db, title=book.title)
    if is_book_reg:
        raise HTTPException(status_code=400, detail="Book already added")
    return crud.add_book(db=db, book=book)


# TODO: add update_book_info

@books_router.post("/book/add_form", response_model=schemas.Book, tags=[schemas.Tags.books])
async def add_book_form(background_tasks: BackgroundTasks,
                        title: str = Form(...),
                        writers_str: Optional[str] = Form(default=None),
                        description: Optional[str] = Form(default=None),
                        publish_date: datetime.date = Form(default=datetime.date.today()),
                        rating: Optional[int] = Form(default=None),
                        cover_filename: Optional[str] = Form(default=None),
                        book_filename: Optional[str] = Form(default=None),
                        genres_str: Optional[str] = Form(default=None),
                        cover_file: Optional[UploadFile] = File(default=None),
                        book_file: UploadFile = File(...),
                        db: Session = Depends(dependencies.get_db)):
    if cover_filename is None:
        cover_filepath = cwd / "media" / "covers" / f"{cover_file.filename}"
        cover_file.filename = cover_filepath
    else:
        cover_file.filename = cwd / "media" / "covers" / f"{cover_filename}{pathlib.Path(cover_file.filename).suffix}"

    if book_filename is None:
        book_filepath = cwd / "media" / "books" / f"{book_file.filename}"
        book_file.filename = book_filepath
    else:
        book_file.filename = cwd / "media" / "books" / f"{book_filename}{pathlib.Path(book_file.filename).suffix}"

    if cover_file.content_type == 'image/png' \
            or cover_file.content_type == 'image/jpeg':
        background_tasks.add_task(crud.save_file, cover_file)
    else:
        raise HTTPException(status_code=418, detail="Unsupported format, must be .jpg or .png")

    if book_file.content_type == 'application/epub+zip' \
            or book_file.content_type == 'text/plain' \
            or book_file.content_type == 'application/pdf':
        book_file.filename = cwd / "media" / "books" / f"{book_file.filename}"
        background_tasks.add_task(crud.save_file, book_file)
    else:
        raise HTTPException(status_code=418, detail="Unsupported format, must be .epub / .txt / .pdf ")

    is_book_reg = crud.get_book_by_title(db, title=title)
    if is_book_reg:
        raise HTTPException(status_code=400, detail="Book already added")
    cover_file_db_format_name = str(pathlib.Path(*cover_file.filename.parts[-2:]))
    book_file_db_format_name = str(pathlib.Path(*book_file.filename.parts[-2:]))

    db_book = models.Book(title=title,
                          description=description,
                          publish_date=publish_date,
                          rating=rating,
                          cover_file=cover_file_db_format_name,
                          book_file=book_file_db_format_name)

    db_book, writers, genres = crud.add_book_with_entities(db=db, db_book=db_book,
                                                           writers_str=writers_str,
                                                           genres_str=genres_str)
    db.refresh(db_book)
    book = schemas.Book(**db_book.__dict__)
    book.writer = [' '.join(x) for x in writers]
    book.genres = genres
    return book


@books_router.delete("/book/{book_id}", dependencies=[Depends(allow_create_and_delete_resource)],
                     tags=[schemas.Tags.books])
async def delete_book(book_id: int, db: Session = Depends(dependencies.get_db)):
    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    deleted = crud.delete_book_by_id(db, book)
    if deleted:
        return {"deleted_book": book}
    else:
        raise HTTPException(status_code=404, detail="Unexpected error")
