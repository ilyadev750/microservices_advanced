from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import UserIdDep, UserLogoutDep, DBDep
from src.database import async_session_maker, async_session_maker_null_pull
from src.schemas.users import UserRequestAdd, UserAdd
from src.config import settings
from src.repositories.users import UsersRepository
from src.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(
    data: UserRequestAdd,
    db: DBDep,
):
    auth_service = AuthService()
    user = await db.users.get_one_or_none(email=data.email)
    if user:
        raise HTTPException(
            status_code=409, detail="Пользователь с таким email уже существует!"
        )

    try:
        hashed_password = auth_service.hash_password(data.password)
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный пароль")

    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)

    try:
        await db.users.add(new_user_data)
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Пользователь с таким email уже существует!"
        )

    return {"status": "OK"}


@router.post("/login")
async def login_user(
    data: UserRequestAdd,
    db: DBDep,
    response: Response,
):
    auth_service = AuthService()
    user = await db.users.get_user_with_hashed_password(email=data.email)

    if not user:
        raise HTTPException(
            status_code=401, detail="Пользователь с таким email не зарегистрирован"
        )

    try:
        is_password_correct = auth_service.verify_password(
            data.password, user.hashed_password
        )
    except ValueError:
        is_password_correct = False

    if not is_password_correct:
        raise HTTPException(status_code=401, detail="Пароль неверный")

    access_token = auth_service.create_access_token({"user_id": user.id})
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
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user


@router.post("/logout")
async def logout(
    user_loguot: UserLogoutDep,
):
    return {"success": "Вы успешно вышли из системы!"}


@router.get("/")
def root():
    return {"message": "API is running"}