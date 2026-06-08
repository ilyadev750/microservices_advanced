from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from src.services.base import BaseService
from src.config import settings
from src.exceptions import ErrorTokenHTTPException


class AuthService(BaseService):
    pwd_context = CryptContext(
        schemes=["bcrypt_sha256"],
        deprecated="auto",
    )

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.exceptions.InvalidTokenError:
            raise ErrorTokenHTTPException
