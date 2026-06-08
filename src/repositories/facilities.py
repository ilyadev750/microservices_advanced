from sqlalchemy.exc import IntegrityError
from src.repositories.base import BaseRepository
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.mappers.mappers import FacilityDataMapper, RoomFacilityDataMapper
from src.schemas.facilities import RoomFacilityAdd
from sqlalchemy import select, delete, insert
from pydantic import BaseModel
from src.repositories.utils import get_result_list_from_two
from src.exceptions import FacilityNotExistHTTPException


class FacilityRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityDataMapper

    async def get_existing_ids(self, ids: set[int]):
        query = select(self.model.id).where(self.model.id.in_(ids))
        result = await self.session.execute(query)
        return set(result.scalars().all())


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    mapper = RoomFacilityDataMapper

    async def get_filtered_facility_ids(self, *filter, **filter_by):
        query = select(self.model.facility_id).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def set_room_facilities(self, room_id, room_data):
        get_current_facilities_ids_query = select(self.model.facility_id).filter_by(
            room_id=room_id
        )
        res = await self.session.execute(get_current_facilities_ids_query)
        current_facility_ids: list[int] = res.scalars().all()

        add_facility_ids = get_result_list_from_two(
            room_data.facilities_ids, current_facility_ids
        )
        delete_facility_ids = get_result_list_from_two(
            current_facility_ids, room_data.facilities_ids
        )

        if add_facility_ids:
            try:
                add_rooms_facilities_data = [
                    RoomFacilityAdd(room_id=room_id, facility_id=f_id)
                    for f_id in add_facility_ids
                ]
                add_data_stmt = insert(self.model).values(
                    [item.model_dump() for item in add_rooms_facilities_data]
                )
                await self.session.execute(add_data_stmt)
            except IntegrityError:
                raise FacilityNotExistHTTPException

        if delete_facility_ids:
            delete_facilities_stmt = delete(self.model).filter(
                self.model.room_id == room_id,
                self.model.facility_id.in_(delete_facility_ids),
            )
            await self.session.execute(delete_facilities_stmt)

    async def delete_bulk(self, room_id, facility_ids: list[BaseModel]):
        stmt = delete(RoomsFacilitiesOrm).where(
            RoomsFacilitiesOrm.room_id == room_id,
            RoomsFacilitiesOrm.facility_id.in_(facility_ids),
        )
        await self.session.execute(stmt)

    async def delete_by_room_id(self, room_id: int):
        stmt = delete(RoomsFacilitiesOrm).where(RoomsFacilitiesOrm.room_id == room_id)
        await self.session.execute(stmt)
