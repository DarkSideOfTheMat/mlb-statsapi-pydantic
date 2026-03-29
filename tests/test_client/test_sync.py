"""Tests for sync MlbClient."""

from __future__ import annotations

import pytest
import respx

from tests.conftest import load_fixture


@pytest.fixture()
def mock_api():
    with respx.mock(base_url="https://statsapi.mlb.com/api") as api:
        yield api


class TestMlbClientGet:
    """Test the generic get() method."""

    def test_get_sports(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient
        from mlb_statsapi.models.sports import SportsResponse

        data = load_fixture("sports")
        mock_api.get("/v1/sports").respond(200, json=data)

        client = MlbClient()
        result = client.get("sports")
        assert isinstance(result, SportsResponse)
        assert result.sports[0].id == 1

    def test_get_with_query_params(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("teams")
        mock_api.get("/v1/teams", params={"sportId": "1"}).respond(200, json=data)

        client = MlbClient()
        result = client.get("teams", sportId="1")
        assert len(result.teams) == 30

    def test_get_with_path_params(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("people_660271")
        mock_api.get("/v1/people/660271").respond(200, json=data)

        client = MlbClient()
        result = client.get("person", personId="660271")
        assert result.people[0].full_name == "Shohei Ohtani"

    def test_get_unknown_endpoint_raises(self):
        from mlb_statsapi.client.sync_client import MlbClient
        from mlb_statsapi.exceptions import MlbApiError

        client = MlbClient()
        with pytest.raises(MlbApiError, match="Unknown endpoint"):
            client.get("bogus_endpoint")

    def test_get_http_error(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient
        from mlb_statsapi.exceptions import MlbApiError

        mock_api.get("/v1/sports").respond(500)

        client = MlbClient()
        with pytest.raises(MlbApiError):
            client.get("sports")


class TestMlbClientHttpErrors:
    """Test HTTP error status codes."""

    @pytest.mark.parametrize(
        "status_code",
        [400, 404, 429, 500, 503],
        ids=["bad_request", "not_found", "rate_limited", "server_error", "unavailable"],
    )
    def test_http_status_error(self, mock_api, status_code):
        from mlb_statsapi.client.sync_client import MlbClient
        from mlb_statsapi.exceptions import MlbApiError

        mock_api.get("/v1/sports").respond(status_code)

        client = MlbClient()
        with pytest.raises(MlbApiError) as exc_info:
            client.get("sports")
        assert exc_info.value.status_code == status_code


class TestMlbClientConvenience:
    """Test typed convenience methods."""

    def test_schedule(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("schedule")
        mock_api.get("/v1/schedule").respond(200, json=data)

        client = MlbClient()
        result = client.schedule(sport_id=1, date="07/01/2024")
        assert len(result.dates) == 1
        assert result.dates[0].games[0].game_pk == 744914

    def test_teams(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("teams")
        mock_api.get("/v1/teams").respond(200, json=data)

        client = MlbClient()
        result = client.teams(sport_id=1)
        assert len(result.teams) == 30

    def test_person(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("people_660271")
        mock_api.get("/v1/people/660271").respond(200, json=data)

        client = MlbClient()
        result = client.person(person_id=660271)
        assert result.people[0].full_name == "Shohei Ohtani"

    def test_standings(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("standings")
        mock_api.get("/v1/standings").respond(200, json=data)

        client = MlbClient()
        result = client.standings(league_id="103,104")
        assert len(result.records) == 6

    def test_boxscore(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("boxscore")
        mock_api.get("/v1/game/744914/boxscore").respond(200, json=data)

        client = MlbClient()
        result = client.boxscore(game_pk=744914)
        assert result.teams.away.team.id == 117

    def test_linescore(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("linescore")
        mock_api.get("/v1/game/744914/linescore").respond(200, json=data)

        client = MlbClient()
        result = client.linescore(game_pk=744914)
        assert len(result.innings) == 9

    def test_league_leaders(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("stats_leaders")
        mock_api.get("/v1/stats/leaders").respond(200, json=data)

        client = MlbClient()
        result = client.league_leaders(leader_categories="homeRuns", season=2024)
        assert len(result.league_leaders) > 0

    def test_game(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("livefeed")
        mock_api.get("/v1.1/game/744914/feed/live").respond(200, json=data)

        client = MlbClient()
        result = client.game(game_pk=744914)
        assert result.game_pk == 744914


class TestHydrateParam:
    """Test that hydrate parameter is correctly passed."""

    def test_hydrate_string(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("schedule_hydrated_team")
        mock_api.get("/v1/schedule").respond(200, json=data)

        client = MlbClient()
        result = client.schedule(sport_id=1, hydrate="team")
        assert result.dates[0].games[0].teams.away.team.abbreviation == "HOU"

    def test_hydrate_list(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("schedule_hydrated_team")
        mock_api.get("/v1/schedule").respond(200, json=data)

        client = MlbClient()
        result = client.schedule(sport_id=1, hydrate=["team", "venue"])
        assert result.dates[0].games[0].teams.away.team.abbreviation == "HOU"

    def test_hydrate_value_helper(self):
        from mlb_statsapi.client._base import ClientMixin

        assert ClientMixin._hydrate_value(None) is None
        assert ClientMixin._hydrate_value("team") == "team"
        assert ClientMixin._hydrate_value(["team", "venue"]) == "team,venue"


class TestMlbClientContext:
    """Test context manager usage."""

    def test_context_manager(self, mock_api):
        from mlb_statsapi.client.sync_client import MlbClient

        data = load_fixture("sports")
        mock_api.get("/v1/sports").respond(200, json=data)

        with MlbClient() as client:
            result = client.get("sports")
            assert result.sports[0].id == 1
