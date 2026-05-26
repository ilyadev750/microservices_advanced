from datetime import date
from fastapi import Query, Body, APIRouter
from sqlalchemy.exc import IntegrityError, NoResultFound
from src.exceptions import (DateFromMoreDateToHTTPException,
                            HotelHasRoomsHTTPException,
                            HotelNotExistHTTPException)
from src.api.dependencies import PaginationDep, DBDep
from src.schemas.hotels import HotelAdd, HotelPATCH
from src.services.hotels import HotelService


router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Расположение, адрес"),
    date_from: date = Query(example="2026-07-26"),
    date_to: date = Query(example="2026-08-04"),
):
    per_page = pagination.per_page or 5

    try:
        result = await HotelService(db).get_filtered_by_time(
            title=title,
            location=location,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
            date_from=date_from,
            date_to=date_to,
        )
        return result
    except DateFromMoreDateToException:
        raise DateFromMoreDateToHTTPException


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
    result = await HotelService(db).get_hotel(hotel_id=hotel_id)
    if not result:
        raise HotelNotExistHTTPException
    return {"status": "OK", "data": result}


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "Отель Сочи 5 звезд у моря",
                    "location": "ул. Моря, 1",
                },
            },
        }
    ),
):
    await HotelService(db).add_hotel(hotel_data)
    return {"status": "OK", "data": hotel_data}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    try:
        await HotelService(db).delete_hotel(hotel_id=hotel_id)
        return {"status": "OK", "data": "Success"}
    except NoResultFound:
        raise HotelNotExistHTTPException
    except IntegrityError as exc:
        await db.session.rollback()
        raise HotelHasRoomsHTTPException


@router.patch("/{hotel_id}")
async def update_hotel_partial(hotel_id: int, db: DBDep, hotel_data: HotelPATCH):
    await HotelService(db).update_hotel_partiall(hotel_data=hotel_data, exclude_unset=True, hotel_id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.put("/{hotel_id}")
async def update_hotel_full(hotel_id: int, db: DBDep, hotel_data: HotelAdd):
    await HotelService(db).update_hotel_full(hotel_data=hotel_data, hotel_id=hotel_id)
    await db.commit()
    return {"status": "OK"}
