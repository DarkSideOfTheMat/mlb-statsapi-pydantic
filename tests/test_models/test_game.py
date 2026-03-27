"""Tests for game models (boxscore, linescore, live feed)."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestLinescoreInning:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.game import LinescoreInning

        data = load_fixture("linescore")
        inning = LinescoreInning.model_validate(data["innings"][0])
        assert inning.num == 1
        assert inning.ordinal_num == "1st"
        assert inning.home.runs == 0
        assert inning.away.runs == 0


class TestLinescoreResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.game import LinescoreResponse

        data = load_fixture("linescore")
        resp = LinescoreResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert resp.current_inning == 9
        assert resp.scheduled_innings == 9
        assert len(resp.innings) == 9

    def test_team_totals(self):
        from mlb_statsapi.models.game import LinescoreResponse

        data = load_fixture("linescore")
        resp = LinescoreResponse.model_validate(data)
        assert resp.teams.away.runs == 3
        assert resp.teams.home.runs == 1
        assert resp.teams.away.is_winner is True
        assert resp.teams.home.is_winner is False


class TestBoxscoreResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.game import BoxscoreResponse

        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")

    def test_team_stats(self):
        from mlb_statsapi.models.game import BoxscoreResponse

        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        away = resp.teams.away
        assert away.team.id == 117  # Astros
        batting = away.team_stats.batting
        assert batting is not None
        assert "runs" in batting
        assert isinstance(batting["runs"], int)

    def test_players_dict(self):
        from mlb_statsapi.models.game import BoxscoreResponse

        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        players = resp.teams.away.players
        assert len(players) > 0
        key = next(iter(players))
        assert key.startswith("ID")
        player = players[key]
        assert player.person.id > 0

    def test_batting_order(self):
        from mlb_statsapi.models.game import BoxscoreResponse

        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        assert len(resp.teams.away.batting_order) > 0

    def test_officials(self):
        from mlb_statsapi.models.game import BoxscoreResponse

        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        assert len(resp.officials) > 0


class TestLiveFeedResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.game import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert resp.game_pk == 744914

    def test_game_data(self):
        from mlb_statsapi.models.game import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.status is not None
        assert resp.game_data.teams is not None
        assert resp.game_data.venue is not None

    def test_live_data(self):
        from mlb_statsapi.models.game import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.live_data.linescore is not None
        assert resp.live_data.boxscore is not None
        assert resp.live_data.plays is not None
