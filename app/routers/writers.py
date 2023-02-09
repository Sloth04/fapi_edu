from typing import List

from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app.internal.users import allow_create_and_delete_resource
import app.crud as crud
import app.dependencies as dependencies
import app.schemas as schemas

writers_router = APIRouter()


@writers_router.get("/writer/{writer_id}/info", response_model=schemas.Writer, tags=[schemas.Tags.writers],
                    summary="Get writer")
def get_writer(writer_id: int, db: Session = Depends(dependencies.get_db)):
    writer = crud.get_writer_by_id(db, writer_id=writer_id)
    if writer is None:
        raise HTTPException(status_code=404, detail="Writer not found")
    return writer


@writers_router.post("/writer/add", response_model=schemas.Writer, tags=[schemas.Tags.writers], summary="Add writer")
def add_writer(writer: schemas.WriterCreate, db: Session = Depends(dependencies.get_db)):
    is_writer_reg = crud.get_writer_by_name(db, name=writer.name, lastname=writer.lastname)
    if is_writer_reg:
        raise HTTPException(status_code=400, detail="Writer already added")
    return crud.add_writer(db=db, writer=writer)


@writers_router.get("/writers/", response_model=List[schemas.Writer], tags=[schemas.Tags.writers])
def get_writers(params: schemas.PaginationQueryParams = Depends(),
                db: Session = Depends(dependencies.get_db)):
    items = crud.get_writers(db, skip=params.skip, limit=params.limit)
    return items


@writers_router.delete("/writer/{writer_id}", dependencies=[Depends(allow_create_and_delete_resource)],
                       tags=[schemas.Tags.writers])
def delete_writer(writer_id: int, db: Session = Depends(dependencies.get_db)):
    writer = crud.get_writer_by_id(db, writer_id=writer_id)
    if writer is None:
        raise HTTPException(status_code=404, detail="Book not found")
    deleted = crud.delete_book_by_id(db, writer)
    if deleted:
        return {"deleted_writer": writer}
    else:
        raise HTTPException(status_code=404, detail="Unexpected error")
