from fastapi import Body, APIRouter, Depends
from fastapi_cache.decorator import cache
from src.api.dependencies import DBDep, get_current_user_id
from src.schemas.facilities import FacilityAdd
from src.services.facilities import FacilitiesService


router = APIRouter(
    prefix="/facilities",
    tags=["Удобства"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("")
@cache(expire=3)
async def get_all_facilities(db: DBDep):
    # test_task.delay()
    return await FacilitiesService(db).get_all_facilities()


@router.post("")
async def create_facility(
    db: DBDep,
    facility_data: FacilityAdd = Body(
        openapi_examples={
            "1": {"summary": "Удобство", "value": {"title": "Чайник"}},
        }
    ),
):
    await FacilitiesService(db).create_facility(facility_data)
    return {"status": "OK", "data": facility_data}
