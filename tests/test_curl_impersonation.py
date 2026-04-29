import asyncio

import pytest
from curl_cffi.requests import AsyncSession, Session


def test_sync_impersonate_146():
    """Verify synchronous chrome146 impersonation works by making a request."""
    with Session(impersonate="chrome146") as s:
        resp = s.get("https://www.google.com", timeout=10)
        assert resp.status_code == 200
        # curl_cffi should have sent a Chrome 146-like UA
        # We can't easily check the SENT headers without a mock server,
        # but the fact that it didn't crash means chrome146 is a valid target.


def test_async_impersonate_146():
    """Verify asynchronous chrome146 impersonation works."""

    async def run():
        async with AsyncSession(impersonate="chrome146") as s:
            resp = await s.get("https://www.google.com", timeout=10)
            assert resp.status_code == 200

    asyncio.run(run())


if __name__ == "__main__":
    pytest.main([__file__])
