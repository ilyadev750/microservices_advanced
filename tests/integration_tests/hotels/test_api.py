import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


async def test_get_hotels(auth_ac):
    response = await auth_ac.get(
        "/hotels",
        params={
            "date_from": "2026-08-01",
            "date_to": "2026-08-10",
        }
    )
    print(f"{response.json()=}")

    assert response.status_code == 200


async def test_get_hotels_with_date_earlier_than_today(auth_ac):
    response = await auth_ac.get(
        "/hotels",
        params={
            "date_from": "2000-01-01",
            "date_to": "2026-08-10",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Дата заезда и выезда не может быть раньше сегодняшнего дня"


async def test_get_hotels_with_date_from_more_or_equal_date_to(auth_ac):
    response = await auth_ac.get(
        "/hotels",
        params={
            "date_from": "2026-08-10",
            "date_to": "2026-08-10",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Дата заезда должна быть раньше даты выезда"


@pytest.mark.parametrize("cookies", [{}, {"access_token": "invalid-token"}])
async def test_get_hotels_requires_valid_access_token(cookies):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=cookies,
    ) as ac:
        response = await ac.get(
            "/hotels",
            params={
                "date_from": "2026-08-01",
                "date_to": "2026-08-10",
            },
        )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "hotel_data",
    [
        {"title": "", "location": "город Сочи"},
        {"title": "Отель", "location": "город Сочи"},
        {"title": "Отель у моря", "location": ""},
        {"title": "Отель у моря", "location": "Сочи"},
    ],
)
async def test_create_hotel_with_short_title_or_location(auth_ac, hotel_data):
    response = await auth_ac.post("/hotels", json=hotel_data)

    assert response.status_code == 422


@pytest.mark.parametrize("method", ["put", "patch"])
async def test_update_not_existing_hotel(auth_ac, method):
    response = await getattr(auth_ac, method)(
        "/hotels/999999",
        json={
            "title": "Отель у моря",
            "location": "город Сочи",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize("method", ["put", "patch"])
async def test_update_hotel_with_unknown_field(auth_ac, method):
    response = await getattr(auth_ac, method)(
        "/hotels/1",
        json={
            "title": "Отель у моря",
            "location": "город Сочи",
            "unknown_field": "unknown value",
        },
    )

    assert response.status_code == 422


async def test_patch_hotel_with_empty_json(auth_ac):
    response = await auth_ac.patch("/hotels/1", json={})

    assert response.status_code == 204
    assert not response.content


async def test_patch_not_existing_hotel_with_empty_json(auth_ac):
    response = await auth_ac.patch("/hotels/999999", json={})

    assert response.status_code == 404
