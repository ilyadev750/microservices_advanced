from pydantic import BaseModel, Field, ConfigDict, PositiveInt, model_validator
from src.schemas.facilities import Facility


class RoomPut(BaseModel):
    title: str
    description: str
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)
    model_config = ConfigDict(extra="forbid")


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
    price: int | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=0)
    model_config = ConfigDict(extra="forbid")


class RoomAddRequest(RoomPut):
    title: str = Field(min_length=1)
    facilities_ids: list[PositiveInt] | None = None
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class RoomPutRequest(RoomPut):
    title: str = Field(min_length=6)
    facilities_ids: list[PositiveInt]
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class RoomPatchRequest(RoomPATCH):
    facilities_ids: list[PositiveInt] | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_empty_room_fields(cls, data):
        if not isinstance(data, dict):
            return data

        room_fields = ("title", "price", "quantity")
        empty_fields = [
            field
            for field in room_fields
            if field in data and data[field] in (None, "")
        ]
        if "description" in data and data["description"] is None:
            empty_fields.append("description")
        if empty_fields:
            raise ValueError("Поля номера не могут быть пустыми")

        return data
