"""Tests for team models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestTeam:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.teams import Team

        data = load_fixture("teams")
        team = Team.model_validate(data["teams"][0])
        assert team.id == 133
        assert team.name == "Athletics"
        assert team.abbreviation == "ATH"
        assert team.team_name == "Athletics"
        assert team.location_name == "Sacramento"
        assert team.short_name == "Athletics"
        assert team.franchise_name == "Athletics"
        assert team.club_name == "Athletics"
        assert team.active is True
        assert team.first_year_of_play == 1901
        assert team.season == 2026

    def test_venue_reference(self):
        from mlb_statsapi.models.teams import Team

        data = load_fixture("teams")
        team = Team.model_validate(data["teams"][0])
        assert team.venue.id == 2529
        assert team.venue.name == "Sutter Health Park"

    def test_spring_venue_no_name(self):
        from mlb_statsapi.models.teams import Team

        data = load_fixture("teams")
        team = Team.model_validate(data["teams"][0])
        assert team.spring_venue.id == 2507
        assert team.spring_venue.name is None

    def test_league_division_refs(self):
        from mlb_statsapi.models.teams import Team

        data = load_fixture("teams")
        team = Team.model_validate(data["teams"][0])
        assert team.league.id == 103
        assert team.league.name == "American League"
        assert team.division.id == 200
        assert team.division.name == "American League West"

    def test_sport_reference(self):
        from mlb_statsapi.models.teams import Team

        data = load_fixture("teams")
        team = Team.model_validate(data["teams"][0])
        assert team.sport.id == 1

    def test_spring_league(self):
        from mlb_statsapi.models.teams import Team

        data = load_fixture("teams")
        team = Team.model_validate(data["teams"][0])
        assert team.spring_league.id == 114
        assert team.spring_league.name == "Cactus League"


class TestTeamsResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.teams import TeamsResponse

        data = load_fixture("teams")
        resp = TeamsResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.teams) == 30

    def test_all_teams_have_ids(self):
        from mlb_statsapi.models.teams import TeamsResponse

        data = load_fixture("teams")
        resp = TeamsResponse.model_validate(data)
        for team in resp.teams:
            assert isinstance(team.id, int)
            assert team.active is True
