"""Small helpers shared by the acceptance tests."""

from fakeredis import FakeAsyncRedis
from httpx import AsyncClient, Response

PASSWORD = "correct horse battery staple"


async def register(client: AsyncClient, email: str = "alice@example.com") -> Response:
    return await client.post("/auth/register", json={"email": email, "password": PASSWORD})


async def current_otp(redis: FakeAsyncRedis, email: str = "alice@example.com") -> str:
    code = await redis.get(f"otp:{email}")
    assert code is not None, f"no OTP stored under otp:{email}"
    return str(code)


async def register_and_verify(
    client: AsyncClient, redis: FakeAsyncRedis, email: str = "alice@example.com"
) -> None:
    assert (await register(client, email)).status_code == 201
    code = await current_otp(redis, email)
    response = await client.post("/auth/verify-otp", json={"email": email, "code": code})
    assert response.status_code == 200


async def login(
    client: AsyncClient, email: str = "alice@example.com", attempt: str = PASSWORD
) -> Response:
    return await client.post("/auth/login", data={"username": email, "password": attempt})
