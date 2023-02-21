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

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080"]
cwd = pathlib.Path().cwd()


def include_router(app):
    app.include_router(users_router)
    app.include_router(books_router)
    app.include_router(writers_router)


def include_middleware(app):
    app.add_middleware(TimerMiddleware)
    app.add_middleware(CORSMiddleware,
                       allow_origins=origins,
                       allow_credentials=True,
                       allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
                       allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                                      "Access-Control-Allow-Origin",
                                      "Authorization"])


def configure_static(app):
    app.mount("/media", StaticFiles(directory="media"), name="media")


def create_tables():
    models.Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(debug=True)
    include_middleware(app)
    include_router(app)
    configure_static(app)
    create_tables()
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    return app


application = start_application()


@application.get("/")
def root():
    return {"message": "Hello its your main page"}


if __name__ == "__main__":
    uvicorn.run("src.main:application", host="127.0.0.1", port=8080, log_level="debug", reload=True)
