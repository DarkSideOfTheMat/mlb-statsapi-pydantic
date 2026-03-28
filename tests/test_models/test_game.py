"""Tests for game models (boxscore, linescore, live feed)."""

from __future__ import annotations

from mlb_statsapi.models._base import IdNameLink, PersonRef
from mlb_statsapi.models.game import (
    BoxscorePlayer,
    BoxscoreResponse,
    BoxscoreTeam,
    LinescoreInning,
    LinescoreResponse,
)
from tests.conftest import load_fixture


class TestLinescoreInning:
    def test_parse_from_fixture(self):
        data = load_fixture("linescore")
        inning = LinescoreInning.model_validate(data["innings"][0])
        assert inning.num == 1
        assert inning.ordinal_num == "1st"
        assert inning.home.runs == 0
        assert inning.away.runs == 0


class TestLinescoreResponse:
    def test_parse_full_response(self):
        data = load_fixture("linescore")
        resp = LinescoreResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert resp.current_inning == 9
        assert resp.scheduled_innings == 9
        assert len(resp.innings) == 9

    def test_team_totals(self):
        data = load_fixture("linescore")
        resp = LinescoreResponse.model_validate(data)
        assert resp.teams.away.runs == 3
        assert resp.teams.home.runs == 1
        assert resp.teams.away.is_winner is True
        assert resp.teams.home.is_winner is False

    def test_inning_half_enum(self):
        from mlb_statsapi.models.enums import HalfInning

        data = load_fixture("linescore")
        resp = LinescoreResponse.model_validate(data)
        if resp.inning_half is not None:
            valid = (HalfInning.TOP, HalfInning.BOTTOM)
            assert resp.inning_half in valid or isinstance(resp.inning_half, str)


class TestBoxscoreResponse:
    def test_parse_full_response(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")

    def test_team_stats(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        away = resp.teams.away
        assert away.team.id == 117  # Astros
        batting = away.team_stats.batting
        assert batting is not None
        assert "runs" in batting
        assert isinstance(batting["runs"], int)

    def test_players_dict(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        players = resp.teams.away.players
        assert len(players) > 0
        key = next(iter(players))
        assert key.startswith("ID")
        player = players[key]
        assert player.person.id > 0

    def test_batting_order(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        assert len(resp.teams.away.batting_order) > 0

    def test_officials(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        assert len(resp.officials) > 0

    def test_boxscore_info_sections(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        away = resp.teams.away
        assert len(away.info) > 0
        section = away.info[0]
        assert section.title is not None
        assert len(section.field_list) > 0
        assert section.field_list[0].label is not None


class TestBoxscoreTeamResolveIds:
    """Tests for BoxscoreTeam._resolve_ids and player property methods."""

    def _make_team(
        self,
        batters: list[int] | None = None,
        pitchers: list[int] | None = None,
        bench: list[int] | None = None,
        bullpen: list[int] | None = None,
        batting_order: list[int] | None = None,
        player_ids: list[int] | None = None,
    ) -> BoxscoreTeam:
        """Build a minimal BoxscoreTeam with given IDs and matching players."""
        all_ids = set()
        for lst in [batters, pitchers, bench, bullpen, batting_order, player_ids]:
            if lst:
                all_ids.update(lst)
        players = {
            f"ID{pid}": BoxscorePlayer(
                person=PersonRef(id=pid, full_name=f"Player {pid}")
            )
            for pid in all_ids
        }
        return BoxscoreTeam(
            team=IdNameLink(id=1, name="Test", link="/api/v1/teams/1"),
            players=players,
            batters=batters or [],
            pitchers=pitchers or [],
            bench=bench or [],
            bullpen=bullpen or [],
            batting_order=batting_order or [],
        )

    def test_batter_players_resolves(self):
        team = self._make_team(batters=[100, 200, 300])
        result = team.batter_players
        assert len(result) == 3
        assert result[0].person.id == 100
        assert result[1].person.id == 200
        assert result[2].person.id == 300

    def test_pitcher_players_resolves(self):
        team = self._make_team(pitchers=[400, 500])
        result = team.pitcher_players
        assert len(result) == 2
        assert result[0].person.id == 400

    def test_bench_players_resolves(self):
        team = self._make_team(bench=[600])
        result = team.bench_players
        assert len(result) == 1
        assert result[0].person.id == 600

    def test_bullpen_players_resolves(self):
        team = self._make_team(bullpen=[700, 800])
        result = team.bullpen_players
        assert len(result) == 2

    def test_batting_order_players_resolves(self):
        team = self._make_team(batting_order=[100, 200])
        result = team.batting_order_players
        assert len(result) == 2
        assert result[0].person.id == 100

    def test_resolve_ids_skips_missing(self):
        """IDs not present in the players dict are silently skipped."""
        team = self._make_team(player_ids=[100])
        team.batters = [100, 999]  # 999 doesn't exist in players
        result = team.batter_players
        assert len(result) == 1
        assert result[0].person.id == 100

    def test_resolve_ids_empty_list(self):
        team = self._make_team(player_ids=[100])
        assert team.batter_players == []

    def test_resolve_ids_preserves_order(self):
        team = self._make_team(batters=[300, 100, 200])
        ids = [p.person.id for p in team.batter_players]
        assert ids == [300, 100, 200]

    def test_resolve_ids_from_fixture(self):
        """Verify _resolve_ids works with real fixture data."""
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        away = resp.teams.away

        batter_players = away.batter_players
        assert len(batter_players) > 0
        assert len(batter_players) == len(away.batters)
        # First batter should be Alex Bregman (ID 608324)
        assert batter_players[0].person.full_name == "Alex Bregman"

    def test_pitcher_players_from_fixture(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        away = resp.teams.away

        pitcher_players = away.pitcher_players
        assert len(pitcher_players) > 0
        assert len(pitcher_players) == len(away.pitchers)

    def test_bench_players_from_fixture(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        away = resp.teams.away

        bench_players = away.bench_players
        assert len(bench_players) > 0
        assert len(bench_players) == len(away.bench)

    def test_bullpen_players_from_fixture(self):
        data = load_fixture("boxscore")
        resp = BoxscoreResponse.model_validate(data)
        away = resp.teams.away

        bullpen_players = away.bullpen_players
        assert len(bullpen_players) > 0
        assert len(bullpen_players) == len(away.bullpen)
