from datetime import timedelta

import pyotp
from fastapi import Depends, HTTPException, status, Body, BackgroundTasks, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import src.crud as crud
import src.dependencies as dependencies
import src.internal.users as int_users
import src.schemas as schemas
from src.internal.roles import allow_create_and_delete_resource

from settings import *

users_router = APIRouter()


@users_router.post("/token", response_model=schemas.Token, tags=[schemas.Tags.users])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(dependencies.get_db)):
    user = int_users.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = int_users.create_access_token(data={"sub": user.username},
                                                 expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get("/users/me/", response_model=schemas.User, tags=[schemas.Tags.users])
async def read_users_me(
        current_user: schemas.User = Depends(int_users.get_current_active_user)):
    return current_user


@users_router.put("/users/me/", response_model=schemas.User, tags=[schemas.Tags.users])
async def user_update_own_record(user_update: schemas.UserUpdate,
                                 db: Session = Depends(dependencies.get_db),
                                 current_user: schemas.User = Depends(int_users.get_current_active_user)):
    db_user = crud.update_user_self(db, current_user, user_update)
    db_user.qr_code_link = pyotp.totp.TOTP(db_user.otp_secret).provisioning_uri(
        name=db_user.email, issuer_name='Library App')
    logger.debug(f"User {db_user.username} was updated")
    return db_user


@users_router.get("/users/{user_id}", response_model=schemas.User,
                  dependencies=[Depends(allow_create_and_delete_resource)], tags=[schemas.Tags.users])
async def get_user_by_id(
        user_id: int,
        db: Session = Depends(dependencies.get_db),
        current_user: schemas.User = Depends(int_users.get_current_active_admin_user)):
    db_user = crud.get_user(db, user_id)
    db_user.qr_code_link = pyotp.totp.TOTP(db_user.otp_secret).provisioning_uri(
        name=db_user.email, issuer_name='Library App')
    return db_user


@users_router.post("/users/", response_model=schemas.User, tags=[schemas.Tags.users])
async def create_new_user(
        background_tasks: BackgroundTasks,
        user: schemas.UserCreate = Body(
            example={
                "username": "test_user",
                "email": "test_user@example.com",
                "full_name": "Test User",
                "password": "pass",
                "role": "user",
            }
        ),
        db: Session = Depends(dependencies.get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is taken")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is used")
    db_user = crud.create_user(db, user)
    db_user.qr_code_link = pyotp.totp.TOTP(db_user.otp_secret).provisioning_uri(
        name=db_user.email, issuer_name='Library App')
    qr_code_img = int_users.create_qr_code_img(uri_str=db_user.qr_code_link, username=db_user.username)
    int_users.send_email_background_new_user(background_tasks,
                                             subject='Hello there!',
                                             email_to=db_user.email,
                                             body={'title': 'Hello dear user', 'name': db_user.full_name,
                                                   'qr_code_img': qr_code_img}, template_name='new_user_email.html')
    return db_user
