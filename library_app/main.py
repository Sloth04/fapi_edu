import uvicorn
from fastapi import FastAPI
from library_router import library_router
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello its your app"}


app.include_router(library_router)

if __name__ == "__main__":
    uvicorn.run("library_app.main:app", host="127.0.0.1", port=8080, log_level="debug", reload=True)
