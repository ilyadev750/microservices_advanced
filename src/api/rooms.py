from fastapi import Body, APIRouter, Query, Depends, Response, status
from datetime import date
from sqlalchemy.exc import NoResultFound
from src.api.dependencies import DBDep, get_current_user_id
from src.exceptions import (DateFromMoreDateToException,
                            DateFromMoreDateToHTTPException,
                            DateEarlierThanTodayHTTPException,
                            RoomNotExistException,
                            RoomNotExistHTTPException,
                            HotelNotExistHTTPException)
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPutRequest
from src.services.hotels import HotelService
from src.services.rooms import RoomsService


router = APIRouter(
    prefix="/hotels",
    tags=["Номера"],
    dependencies=[Depends(get_current_user_id)],
)


async def check_hotel_and_room_exists(db: DBDep, hotel_id: int, room_id: int):
    hotel = await HotelService(db).get_hotel(hotel_id=hotel_id)
    if not hotel:
        raise HotelNotExistHTTPException

    try:
        await RoomsService(db).get_one_room(hotel_id=hotel_id, room_id=room_id)
    except RoomNotExistException:
        raise RoomNotExistHTTPException


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2026-07-26"),
    date_to: date = Query(example="2026-07-31"),
):
    if date_from < date.today() or date_to < date.today():
        raise DateEarlierThanTodayHTTPException

    hotel = await HotelService(db).get_hotel(hotel_id=hotel_id)
    if not hotel:
        raise HotelNotExistHTTPException

    try:
        result = await RoomsService(db).get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
        return result
    except DateFromMoreDateToException:
        raise DateFromMoreDateToHTTPException


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_one_room(db: DBDep, hotel_id: int, room_id: int):
    await check_hotel_and_room_exists(db=db, hotel_id=hotel_id, room_id=room_id)
    result = await RoomsService(db).get_one_room(hotel_id=hotel_id, room_id=room_id)
    return result


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
    hotel = await HotelService(db).get_hotel(hotel_id=hotel_id)
    if not hotel:
        raise HotelNotExistHTTPException

    room = await RoomsService(db).add_room(hotel_id=hotel_id, room_data=room_data)
    return {"status": "OK", "data": room_data}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def update_room_partial(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomPatchRequest
):
    await check_hotel_and_room_exists(db=db, hotel_id=hotel_id, room_id=room_id)

    room_fields = room_data.model_dump(
        exclude_unset=True,
        exclude={"facilities_ids"},
    )
    if not room_fields and "facilities_ids" not in room_data.model_fields_set:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    facility_ids = (
        room_data.facilities_ids
        if "facilities_ids" in room_data.model_fields_set
        else None
    )

    result = await RoomsService(db).update_room(
        hotel_id=hotel_id,
        room_id=room_id,
        room_data=room_data,
        facility_ids=facility_ids,
        exclude_unset=True,
    )
    return {
        "status": "OK",
        "add": result["add"],
        "delete": result["delete"],
    }


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room_full(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomPutRequest
):
    await check_hotel_and_room_exists(db=db, hotel_id=hotel_id, room_id=room_id)

    _room_data = RoomAdd(
        hotel_id=hotel_id,
        **room_data.model_dump(exclude={"facilities_ids"}),
    )
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
    await check_hotel_and_room_exists(db=db, hotel_id=hotel_id, room_id=room_id)
    await RoomsService(db).delete_room(hotel_id=hotel_id, room_id=room_id)
    return {"status": "OK", "data": "Success"}
