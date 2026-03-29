"""Tests for standings models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestTeamStanding:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.standings import TeamStanding

        data = load_fixture("standings")
        record = TeamStanding.model_validate(data["records"][0]["teamRecords"][0])
        assert record.team.name == "Yankees"
        assert record.season == 2024
        assert record.division_rank == "1"
        assert record.games_played == 162

    def test_streak(self):
        from mlb_statsapi.models.standings import TeamStanding

        data = load_fixture("standings")
        record = TeamStanding.model_validate(data["records"][0]["teamRecords"][0])
        assert record.streak.streak_code == "W1"
        assert record.streak.streak_type == "wins"
        assert record.streak.streak_number == 1

    def test_league_record(self):
        from mlb_statsapi.models.standings import TeamStanding

        data = load_fixture("standings")
        record = TeamStanding.model_validate(data["records"][0]["teamRecords"][0])
        assert record.league_record.wins == 94
        assert record.league_record.losses == 68
        assert record.league_record.pct == ".580"

    def test_games_back(self):
        from mlb_statsapi.models.standings import TeamStanding

        data = load_fixture("standings")
        record = TeamStanding.model_validate(data["records"][0]["teamRecords"][0])
        assert record.games_back == "-"
        assert record.wild_card_games_back == "-"


class TestStandingsRecord:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.standings import StandingsRecord

        data = load_fixture("standings")
        record = StandingsRecord.model_validate(data["records"][0])
        assert record.standings_type == "regularSeason"
        assert record.league.id == 103
        assert record.division.id == 201
        assert len(record.team_records) > 0


class TestStandingsResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.standings import StandingsResponse

        data = load_fixture("standings")
        resp = StandingsResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.records) == 6

    def test_all_divisions_present(self):
        from mlb_statsapi.models.standings import StandingsResponse

        data = load_fixture("standings")
        resp = StandingsResponse.model_validate(data)
        div_ids = {r.division.id for r in resp.records}
        assert len(div_ids) == 6
