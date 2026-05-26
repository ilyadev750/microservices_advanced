from fastapi import Body, APIRouter, Query
from datetime import date
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.api.dependencies import DBDep
from src.exceptions import (DateFromMoreDateToException,
                            DateFromMoreDateToHTTPException,
                            RoomNotExistException,
                            RoomNotExistHTTPException,
                            HotelNotExistHTTPException)
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest
from src.services.rooms import RoomsService


router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2026-07-26"),
    date_to: date = Query(example="2026-07-31"),
):
    try:
        result = await RoomsService(db).get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
        return result
    except DateFromMoreDateToException:
        raise DateFromMoreDateToHTTPException


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_one_room(db: DBDep, hotel_id: int, room_id: int):
    try:
        result = await RoomsService(db).get_one_room(hotel_id=hotel_id, room_id=room_id)
        return result
    except RoomNotExistException:
        raise RoomNotExistHTTPException


@router.post("/{hotel_id}/rooms")
async def create_room(
    hotel_id: int,
    db: DBDep,
    room_data: RoomAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Эконом номер",
                "value": {
                    "title": "Номер эконом класса",
                    "description": "",
                    "price": 2500,
                    "quantity": 10,
                    "facilities_ids": [1, 2],
                },
            },
        }
    ),
):
    try:
        room = await RoomsService(db).add_room(hotel_id=hotel_id, room_data=room_data)
        return {"status": "OK", "data": room_data}
    except IntegrityError:
        raise HotelNotExistHTTPException


@router.patch("/{hotel_id}/rooms/{room_id}")
async def update_room_partial(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomPatchRequest
):
    facility_ids = await RoomsService(db).update_room(
        hotel_id=hotel_id,
        room_id=room_id,
        room_data=room_data,
        facility_ids=room_data.facilities_ids,
        exclude_unset=True,
    )
    return {
        "status": "OK",
        "add": facility_ids["add"],
        "delete": facility_ids["delete"],
    }


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room_full(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomAddRequest
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    facility_ids = await RoomsService(db).update_room(
        hotel_id=hotel_id,
        room_id=room_id,
        room_data=_room_data,
        facility_ids=room_data.facilities_ids,
    )
    return {
        "status": "OK",
        "add": facility_ids["add"],
        "delete": facility_ids["delete"],
    }


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        await RoomsService(db).delete_room(hotel_id=hotel_id, room_id=room_id)
        return {"status": "OK", "data": "Success"}
    except NoResultFound:
        raise RoomNotExistHTTPException
