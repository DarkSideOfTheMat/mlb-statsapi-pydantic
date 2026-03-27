"""Tests for sports models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestSport:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.sports import Sport

        data = load_fixture("sports")
        sport = Sport.model_validate(data["sports"][0])
        assert sport.id == 1
        assert sport.code == "mlb"
        assert sport.name == "Major League Baseball"
        assert sport.abbreviation == "MLB"
        assert sport.sort_order == 11
        assert sport.active_status is True
        assert sport.link == "/api/v1/sports/1"


class TestSportsResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.sports import SportsResponse

        data = load_fixture("sports")
        resp = SportsResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.sports) > 0
        assert resp.sports[0].id == 1

    def test_all_sports_have_ids(self):
        from mlb_statsapi.models.sports import SportsResponse

        data = load_fixture("sports")
        resp = SportsResponse.model_validate(data)
        for sport in resp.sports:
            assert isinstance(sport.id, int)
            assert sport.link.startswith("/api/v1/sports/")
