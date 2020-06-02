from datetime import datetime, timedelta
from typing import Dict

import bcrypt
import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.domain.user.user import User

JWT_SUBJECT = "access"
ALGORITHM = "HS256"


def create_jwt_token(
    *, jwt_content: Dict[str], secret_key: str, expires_delta: timedelta
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "sub": JWT_SUBJECT})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM).decode()


def get_user_from_token(token: str, secret_key: str) -> User:
    try:
        user_from_jwt = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error

    try:
        return User(**user_from_jwt)
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt() -> str:
    return bcrypt.gensalt().decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)