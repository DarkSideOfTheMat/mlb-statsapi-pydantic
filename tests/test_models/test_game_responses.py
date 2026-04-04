"""Tests for game endpoint response models."""

from __future__ import annotations

from mlb_statsapi.models.game_responses import (
    ColorFeedResponse,
    ContextMetricsResponse,
    GameChangesResponse,
    GameContentResponse,
    TimestampsResponse,
    UniformsResponse,
    WinProbabilityResponse,
)
from mlb_statsapi.models.livefeed import PlayByPlayResponse
from tests.conftest import load_fixture


class TestPlayByPlayResponse:
    def test_parse_full_response(self):
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.all_plays) == 62

    def test_scoring_plays_returns_play_objects(self):
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        scoring = resp.scoring_plays
        assert len(scoring) > 0
        for play in scoring:
            assert play.about.is_scoring_play is True

    def test_scoring_play_indices(self):
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        indices = resp.scoring_play_indices
        assert isinstance(indices, list)
        assert all(isinstance(i, int) for i in indices)
        assert len(resp.scoring_plays) == len(indices)

    def test_scoring_plays_match_indices(self):
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        for idx, play in zip(resp.scoring_play_indices, resp.scoring_plays):
            assert play is resp.all_plays[idx]

    def test_plays_by_inning(self):
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        assert len(resp.plays_by_inning) == 9
        assert resp.plays_by_inning[0].start_index == 0

    def test_current_play(self):
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        assert resp.current_play is not None

    def test_play_result_description(self):
        """Matches the issue's example usage pattern."""
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        descriptions = [
            play.result.description
            for play in resp.all_plays
            if play.result and play.result.description
        ]
        assert len(descriptions) == len(resp.all_plays)

    def test_scoring_plays_skips_out_of_range(self):
        data = load_fixture("play_by_play")
        resp = PlayByPlayResponse.model_validate(data)
        # Manually inject an out-of-range index
        resp.scoring_play_indices.append(99999)
        # Should still work, just skip the bad index
        scoring = resp.scoring_plays
        assert len(scoring) == len(resp.scoring_play_indices) - 1


class TestWinProbabilityResponse:
    def test_parse_response(self):
        data = load_fixture("win_probability")
        resp = WinProbabilityResponse.model_validate(data)
        assert len(resp.root) > 0

    def test_play_has_win_probability_fields(self):
        data = load_fixture("win_probability")
        resp = WinProbabilityResponse.model_validate(data)
        play = resp.root[0]
        assert play.home_team_win_probability is not None
        assert play.away_team_win_probability is not None

    def test_iterable(self):
        data = load_fixture("win_probability")
        resp = WinProbabilityResponse.model_validate(data)
        plays = list(resp)
        assert len(plays) > 0


class TestContextMetricsResponse:
    def test_parse_response(self):
        data = load_fixture("context_metrics")
        resp = ContextMetricsResponse.model_validate(data)
        assert resp.home_win_probability is not None
        assert resp.away_win_probability is not None

    def test_game_field(self):
        data = load_fixture("context_metrics")
        resp = ContextMetricsResponse.model_validate(data)
        assert resp.game is not None


class TestTimestampsResponse:
    def test_parse_response(self):
        resp = TimestampsResponse.model_validate(["20240605_200600", "20240605_200700"])
        assert len(resp.root) == 2
        assert resp.root[0] == "20240605_200600"

    def test_access_via_root(self):
        resp = TimestampsResponse.model_validate(["20240605_200600", "20240605_200700"])
        assert resp.root == ["20240605_200600", "20240605_200700"]


class TestGameChangesResponse:
    def test_parse_response(self):
        data = load_fixture("game_changes")
        resp = GameChangesResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert resp.total_items is not None
        assert resp.total_games is not None

    def test_dates(self):
        data = load_fixture("game_changes")
        resp = GameChangesResponse.model_validate(data)
        assert len(resp.dates) > 0


class TestGameContentResponse:
    def test_parse_response(self):
        data = load_fixture("game_content")
        resp = GameContentResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")

    def test_highlights(self):
        data = load_fixture("game_content")
        resp = GameContentResponse.model_validate(data)
        assert resp.highlights is not None
        hl = resp.highlights.highlights
        assert hl is not None
        assert len(hl.items) > 0

    def test_highlight_item_fields(self):
        data = load_fixture("game_content")
        resp = GameContentResponse.model_validate(data)
        item = resp.highlights.highlights.items[0]
        assert item.headline is not None
        assert item.type is not None

    def test_highlight_playbacks(self):
        data = load_fixture("game_content")
        resp = GameContentResponse.model_validate(data)
        item = resp.highlights.highlights.items[0]
        assert len(item.playbacks) > 0
        assert item.playbacks[0].url is not None

    def test_media(self):
        data = load_fixture("game_content")
        resp = GameContentResponse.model_validate(data)
        assert resp.media is not None
        assert len(resp.media.epg) > 0

    def test_editorial(self):
        data = load_fixture("game_content")
        resp = GameContentResponse.model_validate(data)
        assert resp.editorial is not None


class TestColorFeedResponse:
    def test_parse_empty(self):
        resp = ColorFeedResponse.model_validate({"items": []})
        assert resp.items == []

    def test_parse_with_items(self):
        resp = ColorFeedResponse.model_validate(
            {"items": [{"type": "play"}, {"type": "action"}]}
        )
        assert len(resp.items) == 2
        assert resp.items[0].type == "play"


class TestUniformsResponse:
    def test_parse_response(self):
        data = load_fixture("uniforms")
        resp = UniformsResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert len(resp.uniforms) > 0

    def test_uniform_teams(self):
        data = load_fixture("uniforms")
        resp = UniformsResponse.model_validate(data)
        uniform = resp.uniforms[0]
        assert uniform.game_pk is not None
        assert uniform.home is not None
        assert uniform.away is not None

    def test_uniform_assets(self):
        data = load_fixture("uniforms")
        resp = UniformsResponse.model_validate(data)
        home = resp.uniforms[0].home
        assert len(home.uniform_assets) > 0
        asset = home.uniform_assets[0]
        assert asset.uniform_asset_code is not None
