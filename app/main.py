import pathlib
import uvicorn
import app.models as models
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqladmin import Admin
from app.internal.admin import UserAdmin
from app.routers import writers_router, books_router, users_router
from database import engine
from middleware import TimerMiddleware
from settings import logger

origins = ["http://localshost:8080"]

cwd = pathlib.Path().cwd()
models.Base.metadata.create_all(bind=engine)

application = FastAPI(debug=True)

admin = Admin(application, engine)
admin.add_view(UserAdmin)

application.include_router(users_router)
application.include_router(books_router)
application.include_router(writers_router)

application.add_middleware(TimerMiddleware)
application.add_middleware(CORSMiddleware, allow_origins=origins)


@application.get("/")
def root():
    return {"message": "Hello its your app"}


if __name__ == "__main__":
    uvicorn.run("app.main:application", host="127.0.0.1", port=8080, log_level="debug", reload=True)
