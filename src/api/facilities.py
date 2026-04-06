from fastapi import Body, APIRouter
from fastapi_cache.decorator import cache
from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd


router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=3)
async def get_all_facilities(db: DBDep):
    # test_task.delay()
    return await db.facilities.get_all()


@router.post("")
async def create_facility(db: DBDep,
                          facility_data: FacilityAdd = Body(openapi_examples={
        "1": {
            "summary": "Удобство",
            "value": {
                "title": "Чайник"
            }
        },
    })
    ):
    await db.facilities.add(facility_data)
    await db.commit()
    return {"status": "OK", "data": facility_data}