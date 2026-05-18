from sqlalchemy import select, func
from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from src.repositories.mappers.mappers import HotelDataMapper
from src.exceptions import DateFromMoreDateToException
from datetime import date
from src.models.rooms import RoomsOrm
from src.repositories.utils import rooms_ids_for_booking


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_filtered_by_time(
        self,
        location,
        title,
        limit,
        offset,
        date_from: date,
        date_to: date,
    ):

        if date_from >= date_to:
            raise DateFromMoreDateToException

        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        if title:
            query = (
                select(HotelsOrm)
                .filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
                .filter(HotelsOrm.id.in_(hotels_ids_to_get))
            )

        elif location:
            query = (
                select(HotelsOrm)
                .filter(
                    func.lower(HotelsOrm.location).contains(location.strip().lower())
                )
                .filter(HotelsOrm.id.in_(hotels_ids_to_get))
            )

        else:
            query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))

        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]
