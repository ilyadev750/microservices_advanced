from datetime import date
from sqlalchemy.exc import NoResultFound
from src.schemas.hotels import HotelAdd, HotelPATCH
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_filtered_by_time(
            self,
            location: str | None,
            title: str | None,
            date_from: date,
            date_to: date,
            limit: int,
            offset: int
    ):

        return await self.db.hotels.get_filtered_by_time(
            title=title,
            location=location,
            limit=limit,
            offset=offset,
            date_from=date_from,
            date_to=date_to,
        )

    async def get_hotel(self, hotel_id: int):
        return await self.db.hotels.get_one_or_none(id=hotel_id)

    async def add_hotel(self, data: HotelAdd):
        hotel = await self.db.hotels.add(data)
        await self.db.commit()
        return hotel

    async def update_hotel_full(self, hotel_id: int, hotel_data: HotelAdd):
        await self.db.hotels.update(hotel_data, id=hotel_id)
        await self.db.commit()

    async def update_hotel_partiall(self, hotel_id: int, hotel_data: HotelPATCH, exclude_unset: bool = True):
        if not hotel_data.model_dump(exclude_unset=exclude_unset):
            hotel = await self.db.hotels.get_one_or_none(id=hotel_id)
            if not hotel:
                raise NoResultFound
            return False

        await self.db.hotels.update(hotel_data, exclude_unset=exclude_unset, id=hotel_id)
        await self.db.commit()
        return True

    async def delete_hotel(self, hotel_id: int):
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
