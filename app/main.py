import uvicorn
import crud
import models
import schemas
import pyotp
from datetime import datetime, timedelta
from typing import Optional
from sqladmin import Admin, ModelView
from database import engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt

from settings import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from security import pwd_context
from app.library_app import library_router, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
admin = Admin(app, engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.id, models.User.username, models.User.email, models.User.role, models.User.disable]


admin.add_view(UserAdmin)


@app.get("/")
def root():
    return {"message": "Hello its your app"}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return crud.get_user_by_username(db, username)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password[:-6], user.hashed_password):
        return False
    totp = pyotp.TOTP(user.otp_secret)
    if not totp.verify(password[-6:]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
        current_user: schemas.User = Depends(get_current_user)):
    if current_user.disable:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_admin_user(
        current_user: schemas.User = Depends(get_current_active_user), ):
    if current_user.role != schemas.Role.admin:
        raise HTTPException(status_code=400,
                            detail="User has insufficient permissions")
    return current_user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
        current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.put("/users/me/", response_model=schemas.User)
def user_update_own_record(user_update: schemas.UserUpdate, db: Session = Depends(get_db),
                           current_user: schemas.User = Depends(get_current_active_user)):
    db_user = crud.update_user_self(db, current_user, user_update)
    return db_user


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_active_admin_user)):
    db_user = crud.get_user(db, user_id)
    db_user.qr_code_link = pyotp.totp.TOTP(db_user.otp_secret).provisioning_uri(
        name=db_user.email, issuer_name='Library App')
    return db_user


@app.post("/users/", response_model=schemas.User)
def create_new_user(
        user: schemas.UserCreate = Body(
            example={
                "username": "test_user",
                "email": "test_user@example.com",
                "full_name": "Test User",
                "password": "pass",
                "role": "user",
            }),
        db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    db_user.qr_code_link = pyotp.totp.TOTP(db_user.otp_secret).provisioning_uri(
        name=db_user.email, issuer_name='Library App')
    return db_user


app.include_router(library_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, log_level="debug", reload=True)
