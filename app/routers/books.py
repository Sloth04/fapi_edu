import datetime
import pathlib
import app.crud as crud
import app.models as models
import app.dependencies as dependencies
import app.schemas as schemas
from typing import Optional, List
from fastapi import HTTPException, Depends, APIRouter, Form, UploadFile, File, Request
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse
from app.internal.roles import allow_create_and_delete_resource
from settings import cwd

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
    file = pathlib.Path(book.book_file)
    if file.exists():
        return FileResponse(file, filename=file.name)
    else:
        raise HTTPException(status_code=404, detail="Book file not found")


@books_router.get("/books/", response_model=List[schemas.Book], tags=[schemas.Tags.books])
async def get_books(request: Request,
                    params: schemas.PaginationQueryParams = Depends(),
                    db: Session = Depends(dependencies.get_db)):
    items = crud.get_books(db, skip=params.skip, limit=params.limit)
    for index in range(len(items)):
        cover_file = pathlib.Path(items[index].cover_file)
        items[index].cover_file = request.url_for(f"{cover_file.name}", img=items[index].cover_file)
    return items


@books_router.post("/book/add_info", response_model=schemas.Book, tags=[schemas.Tags.books])
async def add_book_info(book: schemas.BookCreate, db: Session = Depends(dependencies.get_db)):
    is_book_reg = crud.get_book_by_title(db, title=book.title)
    if is_book_reg:
        raise HTTPException(status_code=400, detail="Book already added")
    return crud.add_book(db=db, book=book)


@books_router.post("/book/add_form", response_model=schemas.Book, tags=[schemas.Tags.books])
async def add_book_form(background_tasks: BackgroundTasks,
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
                        db: Session = Depends(dependencies.get_db)):
    if cover_filename is None:
        cover_filename = cwd / "static" / "covers" / f"{cover_file.filename}"
        cover_file.filename = cover_filename
    else:
        cover_file.filename = cwd / "static" / "covers" / f"{cover_filename}{pathlib.Path(cover_file.filename).suffix}"

    if book_filename is None:
        book_filename = cwd / "static" / "books" / f"{book_file.filename}"
        book_file.filename = book_filename
    else:
        book_file.filename = cwd / "static" / "books" / f"{book_filename}{pathlib.Path(book_file.filename).suffix}"

    if cover_file.content_type == 'image/png' or cover_file.content_type == 'image/jpeg':
        background_tasks.add_task(crud.save_file, cover_file)
    else:
        raise HTTPException(status_code=418, detail="Unsupported format, must be .jpg or .png")

    if book_file.content_type == 'application/epub+zip' or book_file.content_type == 'text/plain':
        book_file.filename = cwd / "static" / "books" / f"{book_file.filename}"
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
