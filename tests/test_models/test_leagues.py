"""Tests for league models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestLeague:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.leagues import League

        data = load_fixture("leagues")
        league = League.model_validate(data["leagues"][0])
        assert league.id == 103
        assert league.name == "American League"
        assert league.abbreviation == "AL"
        assert league.name_short == "American"
        assert league.num_games == 162
        assert league.num_teams == 15

    def test_has_wildcard(self):
        from mlb_statsapi.models.leagues import League

        data = load_fixture("leagues")
        league = League.model_validate(data["leagues"][0])
        assert league.has_wild_card is True

    def test_season_state(self):
        from mlb_statsapi.models.leagues import League

        data = load_fixture("leagues")
        league = League.model_validate(data["leagues"][0])
        assert isinstance(league.season_state, str)


class TestLeaguesResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.leagues import LeaguesResponse

        data = load_fixture("leagues")
        resp = LeaguesResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.leagues) >= 2
