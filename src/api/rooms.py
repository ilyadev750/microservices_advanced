from fastapi import Body, APIRouter, Query
from datetime import date
from sqlalchemy.exc import NoResultFound, IntegrityError
from fastapi import HTTPException
from src.api.dependencies import DBDep
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPATCH
from src.schemas.facilities import RoomFacilityAdd
from src.repositories.utils import get_result_list_from_two


router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2026-03-10"),
    date_to: date = Query(example="2026-03-15"),
):
    return await db.rooms.get_filtered_by_time(
        hotel_id=hotel_id, date_from=date_from, date_to=date_to
    )


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_one_room(db: DBDep, hotel_id: int, room_id: int):
    return await db.rooms.get_one_or_none(hotel_id=hotel_id, id=room_id)


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
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room = await db.rooms.add(_room_data)

        if room_data.facilities_ids:
            rooms_facilities_data = [
                RoomFacilityAdd(room_id=room.id, facility_id=f_id)
                for f_id in room_data.facilities_ids
            ]
            await db.rooms_facilities.add_bulk(rooms_facilities_data)

        await db.commit()
        return {"status": "OK", "data": room_data}
    except IntegrityError:
        raise HTTPException(
            status_code=422, detail="Отель с указанным в запросе id не существует"
        )


@router.patch("/{hotel_id}/rooms/{room_id}")
async def update_room_partial(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomPatchRequest
):
    _room_data = RoomPATCH(**room_data.model_dump(exclude_unset=True))
    result = await db.rooms.update(
        _room_data, exclude_unset=True, hotel_id=hotel_id, id=room_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Комната с id {room_id} не найденав отеле с id {hotel_id}",
        )

    current_facility_ids = await db.rooms_facilities.get_filtered_facility_ids(
        room_id=room_id
    )

    add_facility_ids = get_result_list_from_two(
        room_data.facilities_ids, current_facility_ids
    )
    delete_facility_ids = get_result_list_from_two(
        current_facility_ids, room_data.facilities_ids
    )

    await db.rooms_facilities.set_room_facilities(room_id=room_id, room_data=room_data)

    await db.commit()
    return {"status": "OK", "add": add_facility_ids, "delete": delete_facility_ids}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room_full(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomAddRequest
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    result = await db.rooms.update(_room_data, hotel_id=hotel_id, id=room_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Комната с id {room_id} не найдена в отеле с id {hotel_id}",
        )

    current_facility_ids = await db.rooms_facilities.get_filtered_facility_ids(
        room_id=room_id
    )

    add_facility_ids = get_result_list_from_two(
        room_data.facilities_ids, current_facility_ids
    )
    delete_facility_ids = get_result_list_from_two(
        current_facility_ids, room_data.facilities_ids
    )

    await db.rooms_facilities.set_room_facilities(room_id=room_id, room_data=room_data)
    await db.commit()
    return {"status": "OK", "add": add_facility_ids, "delete": delete_facility_ids}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep):

    try:
        await db.rooms.delete(hotel_id=hotel_id, id=room_id)
        await db.commit()
        return {"status": "OK", "data": "Success"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Room with id {room_id} not found")
