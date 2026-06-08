from pydantic import BaseModel, ConfigDict, Field


class HotelAdd(BaseModel):
    title: str = Field(min_length=6)
    location: str = Field(min_length=6)
    model_config = ConfigDict(extra="forbid")


class Hotel(HotelAdd):
    id: int


class HotelPATCH(BaseModel):
    title: str | None = Field(None, min_length=6)
    location: str | None = Field(None, min_length=6)
    model_config = ConfigDict(extra="forbid")
