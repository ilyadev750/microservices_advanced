from datetime import date
from fastapi import Query, Body, APIRouter
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from src.api.dependencies import PaginationDep, DBDep
from src.schemas.hotels import HotelAdd, HotelPATCH


router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Расположение, адрес"),
    date_from: date = Query(example="2025-04-01"),
    date_to: date = Query(example="2025-04-10"),
):
    per_page = pagination.per_page or 5
    # return await db.hotels.get_all(
    #     location=location,
    #     title=title,
    #     limit=per_page,
    #     offset=per_page * (pagination.page - 1)
    # )

    return await db.hotels.get_filtered_by_time(
        title=title,
        location=location,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
    result = await db.hotels.get_one_or_none(id=hotel_id)
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
    await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "data": hotel_data}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep):
    try:
        await db.hotels.delete(id=hotel_id)
        await db.commit()
        return {"status": "OK", "data": "Success"}
    except NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"Hotel with id {hotel_id} not found"
        )


@router.patch("/{hotel_id}")
async def update_hotel_partial(hotel_id: int, db: DBDep, hotel_data: HotelPATCH):
    await db.hotels.update(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.put("/{hotel_id}")
async def update_hotel_full(hotel_id: int, db: DBDep, hotel_data: HotelAdd):
    await db.hotels.update(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}
