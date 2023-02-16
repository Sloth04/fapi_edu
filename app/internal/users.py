from datetime import datetime, timedelta
from typing import Optional

import pyotp
import qrcode
from fastapi import Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import MessageSchema, MessageType
from jose import JWTError, jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session

import app.crud as crud
import app.dependencies as dependencies
import app.schemas as schemas
from .email import send_email_background_task
from app.security import pwd_context
from settings import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
                     db: Session = Depends(dependencies.get_db)):
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


def create_qr_code_img(uri_str: str, username: str):
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(uri_str)
    qr_code_img = qr.make_image()

    current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
    qr_codes_path = cwd / "static" / "qr_codes"
    qr_codes_path.mkdir(parents=True, exist_ok=True)
    qr_filename = qr_codes_path / f'{username}_{current_datetime}.png'
    qr_code_img.save(qr_filename)
    return qr_filename


def send_email_background_new_user(background_tasks: BackgroundTasks,
                                   subject: str,
                                   email_to: EmailStr,
                                   body: dict,
                                   template_name: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype=MessageType.html,
        attachments=[
            {
                "file": "{filepath}".format(filepath=body['qr_code_img']),
                "headers": {
                    "Content-ID": "<qr_image@fastapi-mail>",
                    "Content-Disposition": "inline; filename=\"{filename}\"".format(
                        filename=body['qr_code_img'].name),  # For inline images only
                },
                "mime_type": "image",
                "mime_subtype": "png",
            }
        ],
    )
    send_email_background_task(background_tasks=background_tasks, message=message, template_name=template_name)
