from pydantic import BaseModel, Field, ConfigDict
from src.schemas.facilities import Facility


class RoomPut(BaseModel):
    title: str
    description: str
    price: int
    quantity: int


class RoomAdd(RoomPut):
    hotel_id: int


class Room(RoomAdd):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RoomWithRels(Room):
    facilities: list[Facility]


class RoomPATCH(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)


class RoomAddRequest(RoomPut):
    facilities_ids: list[int] | None = []
    model_config = ConfigDict(from_attributes=True)


class RoomPatchRequest(RoomPATCH):
    facilities_ids: list[int] | None = []
