"""Tests for endpoint registry."""

from __future__ import annotations


class TestEndpointDef:
    def test_build_url_simple(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["sports"]
        url = ep.build_url()
        assert url == "https://statsapi.mlb.com/api/v1/sports"

    def test_build_url_with_path_param(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["person"]
        url = ep.build_url(personId="660271")
        assert url == "https://statsapi.mlb.com/api/v1/people/660271"

    def test_build_url_game_live_feed(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["game"]
        url = ep.build_url(gamePk="744914")
        assert url == "https://statsapi.mlb.com/api/v1.1/game/744914/feed/live"

    def test_build_url_boxscore(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["game_boxscore"]
        url = ep.build_url(gamePk="744914")
        assert url == "https://statsapi.mlb.com/api/v1/game/744914/boxscore"

    def test_build_url_team(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["team"]
        url = ep.build_url(teamId="147")
        assert url == "https://statsapi.mlb.com/api/v1/teams/147"

    def test_build_url_team_roster(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["team_roster"]
        url = ep.build_url(teamId="147")
        assert url == "https://statsapi.mlb.com/api/v1/teams/147/roster"

    def test_build_url_standings(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["standings"]
        url = ep.build_url()
        assert url == "https://statsapi.mlb.com/api/v1/standings"

    def test_build_query_params(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["schedule"]
        qp = ep.filter_query_params(sportId="1", date="07/01/2024", bogus="nope")
        assert qp == {"sportId": "1", "date": "07/01/2024"}
        assert "bogus" not in qp

    def test_version_override(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        ep = ENDPOINTS["sports"]
        url = ep.build_url(ver="v2")
        assert url == "https://statsapi.mlb.com/api/v2/sports"


class TestEndpointCoverage:
    def test_all_tier1_endpoints_exist(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        tier1 = [
            "sports", "teams", "team", "people", "person", "schedule",
            "standings", "game", "game_boxscore", "game_linescore",
            "game_playByPlay", "stats_leaders", "team_roster", "seasons",
        ]
        for name in tier1:
            assert name in ENDPOINTS, f"Missing Tier 1 endpoint: {name}"

    def test_all_endpoints_have_url(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        for name, ep in ENDPOINTS.items():
            assert ep.url_template, f"{name} missing url_template"

    def test_game_endpoints_require_game_pk(self):
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        game_eps = [
            "game", "game_boxscore", "game_linescore",
            "game_playByPlay", "game_content",
        ]
        for name in game_eps:
            ep = ENDPOINTS[name]
            assert "gamePk" in ep.path_params, f"{name} missing gamePk"

    def test_endpoint_count(self):
        """Ensure we have all endpoints from the reference library."""
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        assert len(ENDPOINTS) >= 60

    def test_response_models_linked(self):
        """Tier 1 endpoints should have response models."""
        from mlb_statsapi.endpoints.registry import ENDPOINTS

        tier1_with_models = [
            "sports", "teams", "person", "schedule",
            "standings", "game_boxscore", "game_linescore",
            "stats_leaders", "seasons",
        ]
        for name in tier1_with_models:
            ep = ENDPOINTS[name]
            assert ep.response_model is not None, f"{name} missing response_model"
