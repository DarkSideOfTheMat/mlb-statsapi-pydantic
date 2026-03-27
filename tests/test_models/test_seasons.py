"""Tests for season models."""

from __future__ import annotations

import datetime

from tests.conftest import load_fixture


class TestSeason:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.seasons import Season

        data = load_fixture("seasons")
        season = Season.model_validate(data["seasons"][0])
        assert season.season_id == "2024"
        assert season.has_wildcard is True

    def test_date_fields(self):
        from mlb_statsapi.models.seasons import Season

        data = load_fixture("seasons")
        season = Season.model_validate(data["seasons"][0])
        assert season.regular_season_start_date == datetime.date(2024, 3, 20)
        assert season.regular_season_end_date == datetime.date(2024, 9, 30)
        assert season.pre_season_start_date == datetime.date(2024, 1, 1)

    def test_postseason_dates(self):
        from mlb_statsapi.models.seasons import Season

        data = load_fixture("seasons")
        season = Season.model_validate(data["seasons"][0])
        assert season.post_season_start_date == datetime.date(2024, 10, 1)
        assert season.post_season_end_date == datetime.date(2024, 10, 30)

    def test_all_star_date(self):
        from mlb_statsapi.models.seasons import Season

        data = load_fixture("seasons")
        season = Season.model_validate(data["seasons"][0])
        assert season.all_star_date == datetime.date(2024, 7, 16)


class TestSeasonsResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.seasons import SeasonsResponse

        data = load_fixture("seasons")
        resp = SeasonsResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.seasons) >= 1
        assert resp.seasons[0].season_id == "2024"
