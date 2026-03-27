"""Tests for venue models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestVenue:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.venues import Venue

        data = load_fixture("venue_15")
        venue = Venue.model_validate(data["venues"][0])
        assert venue.id == 15
        assert venue.name == "Chase Field"
        assert venue.link == "/api/v1/venues/15"
        assert venue.active is True

    def test_season_field(self):
        from mlb_statsapi.models.venues import Venue

        data = load_fixture("venue_15")
        venue = Venue.model_validate(data["venues"][0])
        assert venue.season == "2026"


class TestVenuesResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.venues import VenuesResponse

        data = load_fixture("venue_15")
        resp = VenuesResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.venues) == 1
        assert resp.venues[0].name == "Chase Field"
