from pydantic import BaseModel, ConfigDict, Field
from datetime import date


class BookingAddRequest(BaseModel):
    room_id: int | None = Field(default=None, exclude=True)
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
