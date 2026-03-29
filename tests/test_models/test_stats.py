"""Tests for stats models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestLeaderCategory:
    def test_parse_from_fixture(self):
        from mlb_statsapi.models.stats import LeaderCategory

        data = load_fixture("stats_leaders")
        cat = LeaderCategory.model_validate(data["leagueLeaders"][0])
        assert cat.leader_category == "homeRuns"
        assert cat.season == 2024
        assert cat.game_type.id == "R"
        assert len(cat.leaders) > 0

    def test_leader_entry(self):
        from mlb_statsapi.models.stats import LeaderCategory

        data = load_fixture("stats_leaders")
        cat = LeaderCategory.model_validate(data["leagueLeaders"][0])
        leader = cat.leaders[0]
        assert leader.rank == 1
        assert leader.value == "58"
        assert leader.person.full_name == "Aaron Judge"
        assert leader.team.id == 147


class TestStatsResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.stats import StatsResponse

        data = load_fixture("stats_leaders")
        resp = StatsResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.league_leaders) > 0
