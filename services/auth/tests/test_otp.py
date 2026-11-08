"""Your own tests for the OTP flow (AC 5). Uses the `redis_client` fixture, which is fakeredis.

Requirements, checked by tests/acceptance/test_ac5_learner_tests.py: at least 4 tests that cover
  - a success case            (name contains "success", "valid" or "correct")
  - a wrong code              (name contains "wrong" or "invalid")
  - expiry / TTL              (name contains "expir" or "ttl")
  - single use                (name contains "single", "reuse", "twice" or "once")
"""

from fakeredis import FakeAsyncRedis

from app.otp import issue_otp


async def test_issue_otp_sets_a_ttl(redis_client: FakeAsyncRedis) -> None:
    """Worked example: the code is stored under otp:{email} and expires."""
    code = await issue_otp(redis_client, "alice@example.com", ttl_seconds=300)
    assert len(code) == 6
    assert 0 < await redis_client.ttl("otp:alice@example.com") <= 300


# TODO (AC 5): test_verify_otp_success ... (correct code returns True)
# TODO (AC 5): test_verify_otp_wrong_code ... (returns False, key untouched)
# TODO (AC 5): test_verify_otp_expired ... (delete the key or let the TTL pass, returns False)
# TODO (AC 5): test_verify_otp_single_use ... (second verification with the same code fails)
