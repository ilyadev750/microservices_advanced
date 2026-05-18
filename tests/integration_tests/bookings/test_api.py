import pytest


@pytest.fixture(scope="module")
async def after_test(db_module):
    await db_module.bookings.delete()
    await db_module.commit()


@pytest.mark.parametrize("room_id, date_from, date_to, status_code", [
    (1, "2026-08-01", "2026-08-10", 200),
    (1, "2026-08-09", "2026-08-11", 200),
    (1, "2026-08-03", "2026-08-12", 200),
    (1, "2026-08-04", "2026-08-13", 200),
    (1, "2026-08-05", "2026-08-14", 200),
    (1, "2026-08-06", "2026-08-15", 409),
    (1, "2026-08-07", "2026-08-25", 409),
])
async def test_add_booking(room_id, date_from, date_to, status_code,
                           db, auth_ac):
    room_id = (await db.rooms.get_all())[0].id
    response = await auth_ac.post(
        f"/bookings/{room_id}",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )
    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.mark.parametrize("room_id, date_from, date_to, booked_rooms", [
    (1, "2026-08-01", "2026-08-10", 1),
    (1, "2026-08-09", "2026-08-11", 2),
    (1, "2026-08-03", "2026-08-12", 3),
])
async def test_add_and_get_my_bookings(
        room_id,
        date_from,
        date_to,
        booked_rooms,
        after_test,
        auth_ac,
):
    response = await auth_ac.post(
        f"/bookings/{room_id}",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        }
    )
    assert response.status_code == 200

    response_my_bookings = await auth_ac.get("/bookings/me")
    assert response_my_bookings.status_code == 200
    assert len(response_my_bookings.json()) == booked_rooms
