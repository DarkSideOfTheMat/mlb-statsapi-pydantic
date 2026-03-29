"""Tests for async AsyncMlbClient."""

from __future__ import annotations

import pytest
import respx

from tests.conftest import load_fixture


@pytest.fixture()
def mock_api():
    with respx.mock(base_url="https://statsapi.mlb.com/api") as api:
        yield api


class TestAsyncMlbClient:
    @pytest.mark.asyncio
    async def test_get_sports(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient
        from mlb_statsapi.models.sports import SportsResponse

        data = load_fixture("sports")
        mock_api.get("/v1/sports").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.get("sports")
            assert isinstance(result, SportsResponse)
            assert result.sports[0].id == 1

    @pytest.mark.asyncio
    async def test_schedule(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("schedule")
        mock_api.get("/v1/schedule").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.schedule(sport_id=1, date="07/01/2024")
            assert len(result.dates) == 1

    @pytest.mark.asyncio
    async def test_person(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("people_660271")
        mock_api.get("/v1/people/660271").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.person(person_id=660271)
            assert result.people[0].full_name == "Shohei Ohtani"

    @pytest.mark.asyncio
    async def test_http_error(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient
        from mlb_statsapi.exceptions import MlbApiError

        mock_api.get("/v1/sports").respond(500)

        async with AsyncMlbClient() as client:
            with pytest.raises(MlbApiError):
                await client.get("sports")
