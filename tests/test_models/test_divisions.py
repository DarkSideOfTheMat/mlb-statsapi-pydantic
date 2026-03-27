"""Tests for division models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestDivision:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.divisions import Division

        data = load_fixture("divisions")
        div = Division.model_validate(data["divisions"][0])
        assert div.id == 200
        assert div.name == "American League West"
        assert div.name_short == "AL West"
        assert div.abbreviation == "ALW"
        assert div.active is True
        assert div.sort_order == 24

    def test_league_reference(self):
        from mlb_statsapi.models.divisions import Division

        data = load_fixture("divisions")
        div = Division.model_validate(data["divisions"][0])
        assert div.league.id == 103
        assert div.league.link == "/api/v1/league/103"

    def test_sport_reference(self):
        from mlb_statsapi.models.divisions import Division

        data = load_fixture("divisions")
        div = Division.model_validate(data["divisions"][0])
        assert div.sport.id == 1


class TestDivisionsResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.divisions import DivisionsResponse

        data = load_fixture("divisions")
        resp = DivisionsResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.divisions) == 6
