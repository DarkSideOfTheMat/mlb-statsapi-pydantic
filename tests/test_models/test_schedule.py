"""Tests for schedule models."""

from __future__ import annotations

import datetime

from tests.conftest import load_fixture


class TestScheduleGame:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.schedule import ScheduleGame

        data = load_fixture("schedule")
        game = ScheduleGame.model_validate(data["dates"][0]["games"][0])
        assert game.game_pk == 744914
        assert game.game_type == "R"
        assert game.season == 2024
        assert game.official_date == datetime.date(2024, 7, 1)

    def test_status(self):
        from mlb_statsapi.models.schedule import ScheduleGame

        data = load_fixture("schedule")
        game = ScheduleGame.model_validate(data["dates"][0]["games"][0])
        assert game.status.abstract_game_state == "Final"
        assert game.status.coded_game_state == "F"
        assert game.status.detailed_state == "Final"

    def test_teams(self):
        from mlb_statsapi.models.schedule import ScheduleGame

        data = load_fixture("schedule")
        game = ScheduleGame.model_validate(data["dates"][0]["games"][0])
        assert game.teams.away.team.id == 117
        assert game.teams.away.team.name == "Houston Astros"
        assert game.teams.away.score == 3
        assert game.teams.away.is_winner is True
        assert game.teams.home.team.id == 141
        assert game.teams.home.team.name == "Toronto Blue Jays"
        assert game.teams.home.score == 1

    def test_league_record(self):
        from mlb_statsapi.models.schedule import ScheduleGame

        data = load_fixture("schedule")
        game = ScheduleGame.model_validate(data["dates"][0]["games"][0])
        assert game.teams.away.league_record.wins == 43
        assert game.teams.away.league_record.losses == 41

    def test_venue(self):
        from mlb_statsapi.models.schedule import ScheduleGame

        data = load_fixture("schedule")
        game = ScheduleGame.model_validate(data["dates"][0]["games"][0])
        assert game.venue.id == 14
        assert game.venue.name == "Rogers Centre"

    def test_day_night(self):
        from mlb_statsapi.models.schedule import ScheduleGame

        data = load_fixture("schedule")
        game = ScheduleGame.model_validate(data["dates"][0]["games"][0])
        assert game.day_night == "day"


class TestScheduleDate:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.schedule import ScheduleDate

        data = load_fixture("schedule")
        sched_date = ScheduleDate.model_validate(data["dates"][0])
        assert sched_date.date == datetime.date(2024, 7, 1)
        assert sched_date.total_games == 3
        assert len(sched_date.games) == 3


class TestScheduleResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.schedule import ScheduleResponse

        data = load_fixture("schedule")
        resp = ScheduleResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert resp.total_games == 3
        assert len(resp.dates) == 1
        assert len(resp.dates[0].games) == 3
