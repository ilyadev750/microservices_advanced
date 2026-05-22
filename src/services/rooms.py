from types import SimpleNamespace
from src.services.base import BaseService
from src.exceptions import RoomNotExistHTTPException
from src.schemas.rooms import RoomAddRequest, RoomAdd
from src.schemas.facilities import RoomFacilityAdd
from datetime import date
from src.repositories.utils import get_result_list_from_two


class RoomsService(BaseService):
    async def get_filtered_by_time(
        self,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ):
        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to,
        )

    async def get_one_room(self, hotel_id: int, room_id: int):
        return await self.db.rooms.get_one_or_none(hotel_id=hotel_id, id=room_id)

    async def add_room(self, hotel_id: int, room_data: RoomAddRequest):
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room = await self.db.rooms.add(_room_data)

        if room_data.facilities_ids:
            rooms_facilities_data = [
                RoomFacilityAdd(room_id=room.id, facility_id=f_id)
                for f_id in room_data.facilities_ids
            ]
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()
        return room_data

    async def update_room(
        self,
        hotel_id: int,
        room_id: int,
        room_data,
        facility_ids: list[int] | None = None,
        exclude_unset: bool = False,
    ):
        room_values = room_data.model_dump(
            exclude_unset=exclude_unset,
            exclude_none=exclude_unset,
            exclude={"facilities_ids"},
        )

        result = None
        if room_values:
            result = await self.db.rooms.update(
                room_values,
                hotel_id=hotel_id,
                id=room_id,
            )
        else:
            result = await self.db.rooms.get_one_or_none(hotel_id=hotel_id, id=room_id)

        if not result:
            raise RoomNotExistHTTPException

        if facility_ids is None:
            await self.db.commit()
            return {"add": [], "delete": []}

        current_facility_ids = await self.db.rooms_facilities.get_filtered_facility_ids(
            room_id=room_id
        )

        add_facility_ids = get_result_list_from_two(facility_ids, current_facility_ids)
        delete_facility_ids = get_result_list_from_two(
            current_facility_ids, facility_ids
        )

        facilities_data = SimpleNamespace(facilities_ids=facility_ids)
        await self.db.rooms_facilities.set_room_facilities(
            room_id=room_id, room_data=facilities_data
        )

        await self.db.commit()

        return {
            "add": add_facility_ids,
            "delete": delete_facility_ids
        }

    async def delete_room(self, hotel_id: int, room_id: int):
        await self.db.rooms_facilities.delete_by_room_id(room_id=room_id)
        await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        await self.db.commit()
