import pytest
from src.schemas.facilities import FacilityAdd, RoomFacilityAdd
from src.schemas.rooms import RoomAdd


async def test_get_rooms_with_date_earlier_than_today(auth_ac):
    response = await auth_ac.get(
        "/hotels/1/rooms",
        params={
            "date_from": "2000-01-01",
            "date_to": "2026-08-10",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Дата заезда и выезда не может быть раньше сегодняшнего дня"


async def test_get_rooms_with_date_from_more_or_equal_date_to(auth_ac):
    response = await auth_ac.get(
        "/hotels/1/rooms",
        params={
            "date_from": "2026-08-10",
            "date_to": "2026-08-10",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Дата заезда должна быть раньше даты выезда"


async def test_get_rooms_with_not_existing_hotel(auth_ac):
    response = await auth_ac.get(
        "/hotels/999999/rooms",
        params={
            "date_from": "2026-08-01",
            "date_to": "2026-08-10",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Отель не найден!"


async def test_get_one_room_with_not_existing_room(auth_ac):
    response = await auth_ac.get("/hotels/1/rooms/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Номер не найден!"


async def test_patch_room_with_empty_json(auth_ac):
    response = await auth_ac.patch("/hotels/1/rooms/1", json={})

    assert response.status_code == 204
    assert not response.content


@pytest.mark.parametrize(
    "room_data",
    [
        {"title": ""},
        {"title": None},
        {"description": None},
        {"price": None},
        {"quantity": None},
    ],
)
async def test_patch_room_with_empty_fields(auth_ac, room_data):
    response = await auth_ac.patch("/hotels/1/rooms/1", json=room_data)

    assert response.status_code == 422


async def test_patch_room_with_empty_description(auth_ac):
    response = await auth_ac.patch("/hotels/1/rooms/1", json={"description": ""})

    assert response.status_code == 200


async def test_patch_room_without_facilities_ids_does_not_delete_facilities(auth_ac, db):
    facility = await db.facilities.add(FacilityAdd(title="Сейф"))
    await db.rooms_facilities.add(RoomFacilityAdd(room_id=1, facility_id=facility.id))
    await db.commit()

    response = await auth_ac.patch(
        "/hotels/1/rooms/1",
        json={"title": "Улучшенный номер с террасой"},
    )

    facility_ids = await db.rooms_facilities.get_filtered_facility_ids(room_id=1)

    assert response.status_code == 200
    assert response.json()["add"] == []
    assert response.json()["delete"] == []
    assert facility.id in facility_ids


@pytest.mark.parametrize(
    "method, url, room_data",
    [
        ("patch", "/hotels/999999/rooms/1", {"title": "Улучшенный номер"}),
        (
            "put",
            "/hotels/999999/rooms/1",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": 2500,
                "quantity": 10,
                "facilities_ids": [],
            },
        ),
    ],
)
async def test_update_room_with_not_existing_hotel(auth_ac, method, url, room_data):
    response = await getattr(auth_ac, method)(url, json=room_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Отель не найден!"


@pytest.mark.parametrize(
    "method, url, room_data",
    [
        ("patch", "/hotels/1/rooms/999999", {"title": "Улучшенный номер"}),
        (
            "put",
            "/hotels/1/rooms/999999",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": 2500,
                "quantity": 10,
                "facilities_ids": [],
            },
        ),
    ],
)
async def test_update_room_with_not_existing_room(auth_ac, method, url, room_data):
    response = await getattr(auth_ac, method)(url, json=room_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Номер не найден!"


async def test_delete_room_with_not_existing_hotel(auth_ac):
    response = await auth_ac.delete("/hotels/999999/rooms/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Отель не найден!"


async def test_delete_room_with_not_existing_room(auth_ac):
    response = await auth_ac.delete("/hotels/1/rooms/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Номер не найден!"


async def test_put_room_with_empty_title(auth_ac):
    response = await auth_ac.put(
        "/hotels/1/rooms/1",
        json={
            "title": "",
            "description": "",
            "price": 2500,
            "quantity": 10,
            "facilities_ids": [],
        },
    )

    assert response.status_code == 422


async def test_put_room_with_short_title(auth_ac):
    response = await auth_ac.put(
        "/hotels/1/rooms/1",
        json={
            "title": "12345",
            "description": "",
            "price": 2500,
            "quantity": 10,
            "facilities_ids": [],
        },
    )

    assert response.status_code == 422


async def test_put_room_can_fix_existing_room_with_empty_title(auth_ac, db):
    room = await db.rooms.add(
        RoomAdd(
            hotel_id=1,
            title="",
            description="",
            price=2500,
            quantity=10,
        )
    )
    await db.commit()

    response = await auth_ac.put(
        f"/hotels/1/rooms/{room.id}",
        json={
            "title": "Номер эконом класса",
            "description": "",
            "price": 2500,
            "quantity": 10,
            "facilities_ids": [],
        },
    )

    assert response.status_code == 200


async def test_put_room_without_facilities_ids(auth_ac):
    response = await auth_ac.put(
        "/hotels/1/rooms/1",
        json={
            "title": "Номер эконом класса",
            "description": "",
            "price": 2500,
            "quantity": 10,
        },
    )

    assert response.status_code == 422


async def test_put_room_with_zero_facility_id(auth_ac):
    response = await auth_ac.put(
        "/hotels/1/rooms/1",
        json={
            "title": "Номер эконом класса",
            "description": "",
            "price": 2500,
            "quantity": 10,
            "facilities_ids": [0],
        },
    )

    assert response.status_code == 422


async def test_put_room_with_not_existing_facility(auth_ac):
    response = await auth_ac.put(
        "/hotels/1/rooms/1",
        json={
            "title": "Номер эконом класса",
            "description": "",
            "price": 2500,
            "quantity": 10,
            "facilities_ids": [999999],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Удобство с одним из указанных id не существует!"


@pytest.mark.parametrize(
    "method, room_data",
    [
        ("patch", {"price": 0}),
        ("patch", {"price": -1}),
        (
            "put",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": 0,
                "quantity": 10,
                "facilities_ids": [],
            },
        ),
        (
            "put",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": -1,
                "quantity": 10,
                "facilities_ids": [],
            },
        ),
    ],
)
async def test_update_room_with_not_positive_price(auth_ac, method, room_data):
    response = await getattr(auth_ac, method)("/hotels/1/rooms/1", json=room_data)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "method, room_data",
    [
        ("patch", {"quantity": -1}),
        (
            "put",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": 2500,
                "quantity": -1,
                "facilities_ids": [],
            },
        ),
    ],
)
async def test_update_room_with_negative_quantity(auth_ac, method, room_data):
    response = await getattr(auth_ac, method)("/hotels/1/rooms/1", json=room_data)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "method, room_data",
    [
        ("patch", {"quantity": 0}),
        (
            "put",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": 2500,
                "quantity": 0,
                "facilities_ids": [],
            },
        ),
    ],
)
async def test_update_room_with_zero_quantity(auth_ac, method, room_data):
    response = await getattr(auth_ac, method)("/hotels/1/rooms/1", json=room_data)

    assert response.status_code == 200


@pytest.mark.parametrize(
    "method, url, room_data",
    [
        (
            "post",
            "/hotels/1/rooms",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": 2500,
                "quantity": 10,
                "facilities_ids": [],
                "unknown_field": "unknown value",
            },
        ),
        ("patch", "/hotels/1/rooms/1", {"title": "Номер эконом класса", "unknown_field": "unknown value"}),
        (
            "put",
            "/hotels/1/rooms/1",
            {
                "title": "Номер эконом класса",
                "description": "",
                "price": 2500,
                "quantity": 10,
                "facilities_ids": [],
                "unknown_field": "unknown value",
            },
        ),
    ],
)
async def test_room_with_unknown_field(auth_ac, method, url, room_data):
    response = await getattr(auth_ac, method)(url, json=room_data)

    assert response.status_code == 422


async def test_create_room_with_not_existing_hotel(auth_ac):
    response = await auth_ac.post(
        "/hotels/999999/rooms",
        json={
            "title": "Номер эконом класса",
            "description": "",
            "price": 2500,
            "quantity": 10,
            "facilities_ids": [],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Отель не найден!"


async def test_create_room_with_not_existing_facility(auth_ac):
    response = await auth_ac.post(
        "/hotels/1/rooms",
        json={
            "title": "Номер эконом класса",
            "description": "",
            "price": 2500,
            "quantity": 10,
            "facilities_ids": [999999],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Удобство с одним из указанных id не существует!"
