from fastapi import APIRouter, HTTPException, Response
from datetime import datetime, timezone, timedelta
from src.api.dependencies import UserIdDep, UserLogoutDep, DBDep
from src.database import async_session_maker, async_session_maker_null_pull
from src.schemas.users import UserRequestAdd, UserAdd
from passlib.context import CryptContext
import jwt
from src.config import settings
from src.repositories.users import UsersRepository
from src.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto",
)

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode |= {"exp": expire}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


@router.post("/register")
async def register_user(
    data: UserRequestAdd,
    db: DBDep,
):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    await db.users.add(new_user_data)
    await db.commit()

    return {"status": "OK"}


@router.post("/login")
async def login_user(
    data: UserRequestAdd,
    db: DBDep,
    response: Response,
):
    user = await db.users.get_user_with_hashed_password(email=data.email)

    if not user:
        raise HTTPException(
            status_code=401, detail="Пользователь с таким email не зарегистрирован"
        )

    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Пароль неверный")

    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(
    user_id: UserIdDep,
):
    if settings.MODE == "TEST":
        as_session_maker = async_session_maker_null_pull
    else:
        as_session_maker = async_session_maker
    async with as_session_maker() as session:
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        return user


@router.delete("/logout")
async def logout(
    user_loguot: UserLogoutDep,
):
    return {"success": "Вы успешно вышли из системы!"}
