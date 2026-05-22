from src.services.base import BaseService
from src.schemas.facilities import FacilityAdd


class FacilitiesService(BaseService):
    async def get_all_facilities(self):
        return await self.db.facilities.get_all()

    async def create_facility(self, facility_data: FacilityAdd):
        await self.db.facilities.add(facility_data)
        await self.db.commit()
        return