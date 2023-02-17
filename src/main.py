import pathlib
import uvicorn
import src.models as models
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from sqladmin import Admin
from src.internal.admin import UserAdmin
from src.routers import writers_router, books_router, users_router
from database import engine
from middleware import TimerMiddleware
from settings import logger

origins = ["http://localshost:8080", "http://localhost:3000"]

cwd = pathlib.Path().cwd()
models.Base.metadata.create_all(bind=engine)

application = FastAPI(debug=True)

admin = Admin(application, engine)
admin.add_view(UserAdmin)

application.mount("/static", StaticFiles(directory="static"), name="static")
application.include_router(users_router)
application.include_router(books_router)
application.include_router(writers_router)

application.add_middleware(TimerMiddleware)
application.add_middleware(CORSMiddleware, allow_origins=origins)


@application.get("/")
def root():
    return {"message": "Hello its your main page"}


if __name__ == "__main__":
    uvicorn.run("src.main:application", host="127.0.0.1", port=8080, log_level="debug", reload=True)
