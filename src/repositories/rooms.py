from src.exceptions import (DateFromMoreDateToException,
                            RoomNotExistException)
from src.repositories.base import BaseRepository
from datetime import date
from src.models.rooms import RoomsOrm
from src.repositories.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from src.repositories.utils import rooms_ids_for_booking


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    # async def get_all(self, hotel_id: int):
    #     query = select(RoomsOrm).filter_by(hotel_id=hotel_id)
    #     result = await self.session.execute(query)
    #     return [self.mapper.map_to_domain_entity(room)
    #             for room in result.scalars().all()]

    async def update(self, data, exclude_unset: bool = False, **filter_by):
        values = (
            data
            if isinstance(data, dict)
            else data.model_dump(exclude_unset=exclude_unset)
        )
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**values)
            .returning(RoomsOrm)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_filtered_by_time(
        self,
        hotel_id,
        date_from: date,
        date_to: date,
    ):

        if date_from >= date_to:
            raise DateFromMoreDateToException

        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)
        return [
            RoomDataWithRelsMapper.map_to_domain_entity(model)
            for model in result.unique().scalars().all()
        ]

    async def get_one_or_none(self, **filter_by):
        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        model = result.unique().scalars().one_or_none()
        if model is None:
            raise RoomNotExistException
        return RoomDataWithRelsMapper.map_to_domain_entity(model)
