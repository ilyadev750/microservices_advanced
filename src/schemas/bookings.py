from pydantic import BaseModel, ConfigDict
from datetime import date


class BookingAddRequest(BaseModel):
    date_from: date
    date_to: date


class BookingAdd(BookingAddRequest):
    room_id: int
    user_id: int
    price: int
    model_config = ConfigDict(from_attributes=True)


class Booking(BookingAddRequest):
    id: int
    room_id: int
    user_id: int
    price: int
    model_config = ConfigDict(from_attributes=True)
