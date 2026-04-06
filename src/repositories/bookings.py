from typing import Sequence

from sqlalchemy import select
from datetime import date
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.models.bookings import BookingsOrm
from src.repositories.utils import rooms_ids_for_booking


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_user_bookings(self, user_id):
        query = select(BookingsOrm).filter_by(user_id=user_id)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(booking)
            for booking in result.scalars().all()
        ]

    async def check_bookings(
        self, room_id: int, hotel_id: int, date_from: date, date_to: date
    ):
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=date_from,
            date_to=date_to,
            hotel_id=hotel_id,
        )
        rooms_ids_to_book_res = await self.session.execute(rooms_ids_to_get)
        rooms_ids_to_book: Sequence[int] = rooms_ids_to_book_res.scalars().all()
        if room_id in rooms_ids_to_book:
            return True

        return False
        # query = (select(BookingsOrm)
        #          .filter_by(room_id=room_id))
        #
        # bookings_1 = (query
        #               .filter(date_from <= BookingsOrm.date_from)
        #               .filter(date_to >= BookingsOrm.date_to))
        # result_1 = await self.session.execute(bookings_1)
        #
        # if result_1.scalars().first():
        #     # print(f"RESULT 1------ ")
        #     return True
        #
        # bookings_2 = (query
        #               .filter(BookingsOrm.date_from <= date_from)
        #               .filter(BookingsOrm.date_to > date_from))
        # result_2 = await self.session.execute(bookings_2)
        #
        # if result_2.scalars().first():
        #     # print(f"RESULT 2------ ")
        #     return True
        #
        # bookings_3 = (query
        #               .filter(BookingsOrm.date_from < date_to)
        #               .filter(BookingsOrm.date_to >= date_to))
        # result_3 = await self.session.execute(bookings_3)
        #
        # if result_3.scalars().first():
        #     # print(f"RESULT 3------ ")
        #     return True
        #
        # return False
