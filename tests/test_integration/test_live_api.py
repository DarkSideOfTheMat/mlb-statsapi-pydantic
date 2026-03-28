"""Integration tests that hit the live MLB Stats API.

Run with: pytest tests/test_integration/ -m integration
"""

from __future__ import annotations

import httpx
import pytest

BASE_URL = "https://statsapi.mlb.com/api/v1"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def http() -> httpx.Client:
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        yield client


class TestSportsLive:
    def test_parse_sports_response(self, http: httpx.Client):
        from mlb_statsapi.models.sports import SportsResponse

        resp = http.get("/sports")
        resp.raise_for_status()
        result = SportsResponse.model_validate(resp.json())
        assert result.copyright.startswith("Copyright")
        assert len(result.sports) > 0
        mlb = next(s for s in result.sports if s.id == 1)
        assert mlb.name == "Major League Baseball"


class TestDivisionsLive:
    def test_parse_divisions_response(self, http: httpx.Client):
        from mlb_statsapi.models.divisions import DivisionsResponse

        resp = http.get("/divisions", params={"sportId": 1})
        resp.raise_for_status()
        result = DivisionsResponse.model_validate(resp.json())
        assert len(result.divisions) == 6
        for div in result.divisions:
            assert div.league.id in (103, 104)


class TestLeaguesLive:
    def test_parse_leagues_response(self, http: httpx.Client):
        from mlb_statsapi.models.leagues import LeaguesResponse

        resp = http.get("/league", params={"sportId": 1})
        resp.raise_for_status()
        result = LeaguesResponse.model_validate(resp.json())
        assert len(result.leagues) >= 2
        ids = {lg.id for lg in result.leagues}
        assert 103 in ids  # AL
        assert 104 in ids  # NL


class TestVenuesLive:
    def test_parse_venue_response(self, http: httpx.Client):
        from mlb_statsapi.models.venues import VenuesResponse

        resp = http.get("/venues/15")  # Chase Field
        resp.raise_for_status()
        result = VenuesResponse.model_validate(resp.json())
        assert len(result.venues) == 1
        assert result.venues[0].name == "Chase Field"


class TestSeasonsLive:
    def test_parse_seasons_response(self, http: httpx.Client):
        from mlb_statsapi.models.seasons import SeasonsResponse

        resp = http.get("/seasons", params={"sportId": 1, "season": 2024})
        resp.raise_for_status()
        result = SeasonsResponse.model_validate(resp.json())
        assert len(result.seasons) >= 1
        assert result.seasons[0].season_id == 2024
        assert result.seasons[0].regular_season_start_date is not None


class TestTeamsLive:
    def test_parse_teams_response(self, http: httpx.Client):
        from mlb_statsapi.models.teams import TeamsResponse

        resp = http.get("/teams", params={"sportId": 1})
        resp.raise_for_status()
        result = TeamsResponse.model_validate(resp.json())
        assert len(result.teams) == 30
        names = {t.abbreviation for t in result.teams}
        assert "NYY" in names
        assert "LAD" in names


class TestPeopleLive:
    def test_parse_person_response(self, http: httpx.Client):
        from mlb_statsapi.models.people import PeopleResponse

        resp = http.get("/people/660271")  # Ohtani
        resp.raise_for_status()
        result = PeopleResponse.model_validate(resp.json())
        assert len(result.people) == 1
        assert result.people[0].full_name == "Shohei Ohtani"
        assert result.people[0].bat_side is not None


class TestBoxscoreLive:
    def test_parse_boxscore_response(self, http: httpx.Client):
        from mlb_statsapi.models.game import BoxscoreResponse

        resp = http.get("/game/744914/boxscore")
        resp.raise_for_status()
        result = BoxscoreResponse.model_validate(resp.json())
        assert result.teams.away.team.id == 117
        assert len(result.teams.away.players) > 0


class TestLinescoreLive:
    def test_parse_linescore_response(self, http: httpx.Client):
        from mlb_statsapi.models.game import LinescoreResponse

        resp = http.get("/game/744914/linescore")
        resp.raise_for_status()
        result = LinescoreResponse.model_validate(resp.json())
        assert len(result.innings) == 9
        assert result.teams.away.runs == 3


class TestStatsLeadersLive:
    def test_parse_leaders_response(self, http: httpx.Client):
        from mlb_statsapi.models.stats import StatsResponse

        resp = http.get(
            "/stats/leaders",
            params={
                "leaderCategories": "homeRuns",
                "season": 2024,
                "sportId": 1,
                "limit": 5,
            },
        )
        resp.raise_for_status()
        result = StatsResponse.model_validate(resp.json())
        assert len(result.league_leaders) > 0
        assert len(result.league_leaders[0].leaders) > 0


class TestScheduleLive:
    def test_parse_schedule_response(self, http: httpx.Client):
        from mlb_statsapi.models.schedule import ScheduleResponse

        resp = http.get(
            "/schedule", params={"sportId": 1, "date": "07/01/2024"}
        )
        resp.raise_for_status()
        result = ScheduleResponse.model_validate(resp.json())
        assert len(result.dates) >= 1
        assert len(result.dates[0].games) >= 1
        game = result.dates[0].games[0]
        assert game.teams.away.team.id is not None
        assert game.status.abstract_game_state == "Final"


class TestStandingsLive:
    def test_parse_standings_response(self, http: httpx.Client):
        from mlb_statsapi.models.standings import StandingsResponse

        resp = http.get(
            "/standings",
            params={"leagueId": "103,104", "season": 2024},
        )
        resp.raise_for_status()
        result = StandingsResponse.model_validate(resp.json())
        assert len(result.records) == 6
        for record in result.records:
            assert len(record.team_records) >= 4
