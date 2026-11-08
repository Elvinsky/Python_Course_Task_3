"""AC 6: structured logs for register, login, OTP issue/verify, without secrets."""

import logging

import pytest
from fakeredis import FakeAsyncRedis
from httpx import AsyncClient

from tests.acceptance.helpers import PASSWORD, current_otp, login, register

EXPECTED_EVENTS = {
    "user_registered",
    "otp_issued",
    "otp_verified",
    "otp_failed",
    "login_succeeded",
    "login_failed",
}


async def test_events_are_logged_and_secrets_are_not(
    client: AsyncClient, redis_client: FakeAsyncRedis, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    await register(client)
    code = await current_otp(redis_client)
    wrong = "000000" if code != "000000" else "111111"
    await client.post(
        "/auth/verify-otp", json={"email": "alice@example.com", "code": wrong}
    )  # otp_failed
    await client.post(
        "/auth/verify-otp", json={"email": "alice@example.com", "code": code}
    )  # otp_verified
    await login(client, attempt="not the password")  # login_failed
    token = (await login(client)).json()["access_token"]  # login_succeeded

    output = caplog.text
    missing = {event for event in EXPECTED_EVENTS if event not in output}
    assert not missing, f"missing log events: {sorted(missing)}"
    assert PASSWORD not in output, "never log passwords"
    assert "not the password" not in output, "never log passwords"
    assert "$argon2" not in output, "never log password hashes"
    assert code not in output and wrong not in output, "never log OTP codes"
    assert token not in output, "never log tokens"
