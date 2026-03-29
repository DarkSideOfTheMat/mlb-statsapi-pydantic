"""Tests for async AsyncMlbClient."""

from __future__ import annotations

import pytest
import respx

from tests.conftest import load_fixture


@pytest.fixture()
def mock_api():
    with respx.mock(base_url="https://statsapi.mlb.com/api") as api:
        yield api


class TestAsyncMlbClientGet:
    """Test the generic get() method."""

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
    async def test_get_with_query_params(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("teams")
        mock_api.get("/v1/teams", params={"sportId": "1"}).respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.get("teams", sportId="1")
            assert len(result.teams) == 30

    @pytest.mark.asyncio
    async def test_get_with_path_params(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("people_660271")
        mock_api.get("/v1/people/660271").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.get("person", personId="660271")
            assert result.people[0].full_name == "Shohei Ohtani"

    @pytest.mark.asyncio
    async def test_get_unknown_endpoint_raises(self):
        from mlb_statsapi.client.async_client import AsyncMlbClient
        from mlb_statsapi.exceptions import MlbApiError

        async with AsyncMlbClient() as client:
            with pytest.raises(MlbApiError, match="Unknown endpoint"):
                await client.get("bogus_endpoint")

    @pytest.mark.asyncio
    async def test_get_http_error(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient
        from mlb_statsapi.exceptions import MlbApiError

        mock_api.get("/v1/sports").respond(500)

        async with AsyncMlbClient() as client:
            with pytest.raises(MlbApiError):
                await client.get("sports")


class TestAsyncMlbClientConvenience:
    """Test typed convenience methods."""

    @pytest.mark.asyncio
    async def test_schedule(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("schedule")
        mock_api.get("/v1/schedule").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.schedule(sport_id=1, date="07/01/2024")
            assert len(result.dates) == 1
            assert result.dates[0].games[0].game_pk == 744914

    @pytest.mark.asyncio
    async def test_teams(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("teams")
        mock_api.get("/v1/teams").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.teams(sport_id=1)
            assert len(result.teams) == 30

    @pytest.mark.asyncio
    async def test_person(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("people_660271")
        mock_api.get("/v1/people/660271").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.person(person_id=660271)
            assert result.people[0].full_name == "Shohei Ohtani"

    @pytest.mark.asyncio
    async def test_standings(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("standings")
        mock_api.get("/v1/standings").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.standings(league_id="103,104")
            assert len(result.records) == 6

    @pytest.mark.asyncio
    async def test_boxscore(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("boxscore")
        mock_api.get("/v1/game/744914/boxscore").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.boxscore(game_pk=744914)
            assert result.teams.away.team.id == 117

    @pytest.mark.asyncio
    async def test_linescore(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("linescore")
        mock_api.get("/v1/game/744914/linescore").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.linescore(game_pk=744914)
            assert len(result.innings) == 9

    @pytest.mark.asyncio
    async def test_league_leaders(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("stats_leaders")
        mock_api.get("/v1/stats/leaders").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.league_leaders(
                leader_categories="homeRuns", season=2024
            )
            assert len(result.league_leaders) > 0

    @pytest.mark.asyncio
    async def test_game(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("livefeed")
        mock_api.get("/v1.1/game/744914/feed/live").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.game(game_pk=744914)
            assert result.game_pk == 744914


class TestAsyncHydrateParam:
    """Test that hydrate parameter is correctly passed."""

    @pytest.mark.asyncio
    async def test_hydrate_string(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("schedule_hydrated_team")
        mock_api.get("/v1/schedule").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.schedule(sport_id=1, hydrate="team")
            assert result.dates[0].games[0].teams.away.team.abbreviation == "HOU"

    @pytest.mark.asyncio
    async def test_hydrate_list(self, mock_api):
        from mlb_statsapi.client.async_client import AsyncMlbClient

        data = load_fixture("schedule_hydrated_team")
        mock_api.get("/v1/schedule").respond(200, json=data)

        async with AsyncMlbClient() as client:
            result = await client.schedule(sport_id=1, hydrate=["team", "venue"])
            assert result.dates[0].games[0].teams.away.team.abbreviation == "HOU"
