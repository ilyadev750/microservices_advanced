from src.services.base import BaseService
from src.schemas.bookings import BookingAdd, BookingAddRequest
from src.exceptions import (
    DateFromMoreDateToHTTPException,
    ObjectNotFoundException,
    RoomNotExistHTTPException,
    DatesAreBusyHTTPException,
)
from src.schemas.bookings import BookingAdd


class BookingsService(BaseService):

    async def get_all_bookings(self):
        return await self.db.bookings.get_all()

    async def get_all_user_bookings(self, user_id: int):
        return await self.db.bookings.get_user_bookings(user_id=user_id)

    async def create_booking(self, user_id: int, room_id: int, booking_data: BookingAddRequest):
        
        if booking_data.date_to <= booking_data.date_from:
            raise DateFromMoreDateToHTTPException

        try:
            room_obj = await self.db.rooms.get_one(id=room_id)
            hotel_id = room_obj.hotel_id
            price = room_obj.price
        except ObjectNotFoundException:
            raise RoomNotExistHTTPException

        is_busy_dates = await self.db.bookings.check_bookings(
            room_id=room_id,
            hotel_id=hotel_id,
            date_from=booking_data.date_from,
            date_to=booking_data.date_to,
        )

        if not is_busy_dates:
            raise DatesAreBusyHTTPException

        _booking_data = BookingAdd(
            user_id=user_id, room_id=room_id, price=price, **booking_data.model_dump()
        )
        await self.db.bookings.add(_booking_data)
        await self.db.commit()
        return _booking_data