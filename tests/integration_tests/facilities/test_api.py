import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


async def login(ac):
    await ac.post(
        "/auth/login",
        json={
            "email": "kot@pes.com",
            "password": "1234567",
        },
    )


async def test_create_facilities(auth_ac):
    await login(auth_ac)

    response_1 = await auth_ac.post(
        "/facilities",
        json={
            "title": "Чайник"
        }
    )
    assert response_1.status_code == 200

    response_2 = await auth_ac.post(
        "/facilities",
        json={
            "title": "Wi-Fi"
        }
    )
    assert response_2.status_code == 200


async def test_create_facility_with_unknown_field(auth_ac):
    await login(auth_ac)

    response = await auth_ac.post(
        "/facilities",
        json={
            "title": "Бассейн",
            "unknown_field": "unknown value",
        },
    )

    assert response.status_code == 422


async def test_get_facilities(auth_ac):
    await login(auth_ac)

    response_1 = await auth_ac.get(
        "/facilities",
    )
    assert len(response_1.json()) == 2


@pytest.mark.parametrize("cookies", [{}, {"access_token": "invalid-token"}])
async def test_get_facilities_requires_valid_access_token(cookies):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies=cookies,
    ) as ac:
        response = await ac.get("/facilities")

    assert response.status_code == 401
