from fastapi import Body, APIRouter, Depends
from fastapi import HTTPException
from src.api.dependencies import DBDep, UserIdDep, get_current_user_id
from src.exceptions import (ObjectNotFoundException,
                            RoomNotExistHTTPException)
from src.schemas.bookings import BookingAdd, BookingAddRequest
from src.services.bookings import BookingsService


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("")
async def get_all_bookings(db: DBDep):
    return await BookingsService(db).get_all_bookings()


@router.get("/me")
async def get_all_user_bookings(db: DBDep, user_id: UserIdDep):
    return await BookingsService(db).get_all_user_bookings(user_id=user_id)


@router.post("/{room_id}")
async def create_booking(
    db: DBDep,
    user_id: UserIdDep,
    room_id: int,
    booking_data: BookingAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Пример",
                "value": {"date_from": "2026-07-26", "date_to": "2026-07-31"},
            },
        }
    ),
):

    _booking_data = await BookingsService(db).create_booking(user_id=user_id, room_id=room_id, booking_data=booking_data)
    return {"status": "OK", "data": _booking_data}
