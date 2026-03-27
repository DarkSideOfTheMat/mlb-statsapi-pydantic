"""Tests for live feed and play-by-play models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestLiveFeedResponse:
    def test_parse_full_response(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert resp.game_pk == 744914

    def test_game_data_status(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.status.abstract_game_state == "Final"
        assert resp.game_data.status.detailed_state == "Final"

    def test_game_data_teams(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.teams.away.id == 117
        assert resp.game_data.teams.home.id == 141

    def test_game_data_venue(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.venue.id == 14

    def test_weather(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.weather is not None

    def test_probable_pitchers(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        pp = resp.game_data.probable_pitchers
        assert pp is not None
        assert pp.away.id > 0
        assert pp.home.id > 0

    def test_decisions(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        decisions = resp.live_data.decisions
        assert decisions.winner.full_name == "Hunter Brown"
        assert decisions.loser.full_name == "Yariel Rodríguez"
        assert decisions.save.full_name == "Josh Hader"


class TestPlays:
    def test_all_plays_parsed(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        plays = resp.live_data.plays
        assert len(plays.all_plays) == 68

    def test_scoring_plays(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.live_data.plays.scoring_plays == [29, 61, 66]

    def test_plays_by_inning(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        pbi = resp.live_data.plays.plays_by_inning
        assert len(pbi) == 9
        assert pbi[0].start_index == 0
        assert len(pbi[0].top) > 0
        assert len(pbi[0].bottom) > 0


class TestPlay:
    def test_play_result(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.result.type == "atBat"
        assert play.result.event == "Flyout"
        assert play.result.event_type == "field_out"
        assert "Bregman" in play.result.description
        assert play.result.is_out is True

    def test_play_about(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.about.at_bat_index == 0
        assert play.about.half_inning == "top"
        assert play.about.is_top_inning is True
        assert play.about.inning == 1
        assert play.about.is_complete is True

    def test_play_count(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.count.balls == 1
        assert play.count.strikes == 1
        assert play.count.outs == 1

    def test_scoring_play_result(self):
        """Verify a home run scoring play has correct scores."""
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        scoring_idx = resp.live_data.plays.scoring_plays[0]
        play = resp.live_data.plays.all_plays[scoring_idx]
        assert play.result.event == "Home Run"
        assert play.result.rbi >= 1
        assert play.about.is_scoring_play is True


class TestMatchup:
    def test_batter_pitcher(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.matchup.batter.full_name == "Alex Bregman"
        assert play.matchup.pitcher.full_name == "Yariel Rodríguez"

    def test_handedness(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.matchup.bat_side.code == "R"
        assert play.matchup.pitch_hand.code == "R"

    def test_splits(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.matchup.splits.batter == "vs_RHP"
        assert play.matchup.splits.pitcher == "vs_RHB"
        assert play.matchup.splits.men_on_base == "Empty"


class TestPlayEvents:
    def test_pitch_event(self):
        """Verify a pitch event has full pitch data."""
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]

        pitches = [e for e in play.play_events if e.is_pitch]
        assert len(pitches) > 0
        pitch = pitches[0]
        assert pitch.pitch_number == 1
        assert pitch.type == "pitch"
        assert pitch.details.call.code == "B"
        assert pitch.details.is_ball is True

    def test_pitch_data_speed(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        pitches = [e for e in play.play_events if e.is_pitch]
        pitch = pitches[0]
        assert pitch.pitch_data.start_speed == 95.9
        assert pitch.pitch_data.end_speed == 89.0

    def test_pitch_data_coordinates(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        pitches = [e for e in play.play_events if e.is_pitch]
        coords = pitches[0].pitch_data.coordinates
        assert coords.p_x is not None
        assert coords.p_z is not None
        assert coords.x is not None
        assert coords.y is not None

    def test_pitch_data_breaks(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        pitches = [e for e in play.play_events if e.is_pitch]
        breaks = pitches[0].pitch_data.breaks
        assert breaks.spin_rate == 2191
        assert breaks.spin_direction == 217
        assert breaks.break_vertical is not None

    def test_pitch_type(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        pitches = [e for e in play.play_events if e.is_pitch]
        assert pitches[0].details.type.code == "FF"
        assert pitches[0].details.type.description == "Four-Seam Fastball"

    def test_action_event(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        actions = [e for e in play.play_events if not e.is_pitch]
        assert len(actions) > 0
        assert actions[0].is_action is True


class TestRunners:
    def test_runner_movement(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert len(play.runners) > 0
        runner = play.runners[0]
        assert runner.movement.is_out is True
        assert runner.movement.out_base == "1B"
        assert runner.movement.out_number == 1

    def test_runner_details(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        runner = play.runners[0]
        assert runner.details.event == "Flyout"
        assert runner.details.runner.full_name == "Alex Bregman"
        assert runner.details.is_scoring_event is False

    def test_fielding_credits(self):
        from mlb_statsapi.models.livefeed import LiveFeedResponse

        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        runner = play.runners[0]
        assert len(runner.credits) > 0
        credit = runner.credits[0]
        assert credit.credit == "f_putout"
        assert credit.position.abbreviation == "CF"
