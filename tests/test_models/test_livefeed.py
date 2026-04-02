"""Tests for live feed and play-by-play models."""

from __future__ import annotations

from mlb_statsapi.models._base import PersonRef
from mlb_statsapi.models.enums import PitchType as PitchTypeEnum
from mlb_statsapi.models.livefeed import (
    Count,
    LiveFeedResponse,
    Matchup,
    Play,
    PlayEvent,
    Plays,
    Runner,
    RunnerMovement,
)
from tests.conftest import load_fixture


class TestLiveFeedResponse:
    def test_parse_full_response(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.copyright.startswith("Copyright")
        assert resp.game_pk == 744914

    def test_game_data_status(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.status.abstract_game_state == "Final"
        assert resp.game_data.status.detailed_state == "Final"

    def test_game_data_teams(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.teams.away.id == 117
        assert resp.game_data.teams.home.id == 141

    def test_game_data_venue(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.venue.id == 14

    def test_weather(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.game_data.weather is not None

    def test_probable_pitchers(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        pp = resp.game_data.probable_pitchers
        assert pp is not None
        assert pp.away.id > 0
        assert pp.home.id > 0

    def test_decisions(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        decisions = resp.live_data.decisions
        assert decisions.winner.full_name == "Hunter Brown"
        assert decisions.loser.full_name == "Yariel Rodríguez"
        assert decisions.save.full_name == "Josh Hader"

    def test_game_info(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        game = resp.game_data.game
        assert game is not None
        assert game.pk == 744914

    def test_game_datetime(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        dt = resp.game_data.datetime
        assert dt is not None
        assert dt.date_time is not None

    def test_game_flags(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        flags = resp.game_data.flags
        assert flags is not None
        assert isinstance(flags.no_hitter, bool)
        assert isinstance(flags.perfect_game, bool)

    def test_players_dict(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        players = resp.game_data.players
        assert players is not None
        assert len(players) > 0
        key = next(iter(players))
        assert key.startswith("ID")


class TestPlays:
    def test_all_plays_parsed(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        plays = resp.live_data.plays
        assert len(plays.all_plays) == 68

    def test_scoring_plays(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        assert resp.live_data.plays.scoring_plays == [29, 61, 66]

    def test_plays_by_inning(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        pbi = resp.live_data.plays.plays_by_inning
        assert len(pbi) == 9
        assert pbi[0].start_index == 0
        assert len(pbi[0].top) > 0
        assert len(pbi[0].bottom) > 0


class TestScoringPlayObjects:
    """Tests for Plays.scoring_play_objects property."""

    def test_scoring_play_objects_from_fixture(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        plays = resp.live_data.plays

        scoring = plays.scoring_play_objects
        assert len(scoring) == 3
        # First scoring play is index 29 — a home run
        assert scoring[0].result.event == "Home Run"
        assert scoring[0].about.is_scoring_play is True

    def test_scoring_play_objects_returns_correct_plays(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        plays = resp.live_data.plays

        # Verify each resolved play matches the index
        for idx, play_obj in zip(plays.scoring_plays, plays.scoring_play_objects):
            assert play_obj is plays.all_plays[idx]

    def test_scoring_play_objects_empty(self):
        plays = Plays(all_plays=[], scoring_plays=[])
        assert plays.scoring_play_objects == []

    def test_scoring_play_objects_skips_out_of_range(self):
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            count=Count(),
        )
        plays = Plays(all_plays=[play], scoring_plays=[0, 5])
        result = plays.scoring_play_objects
        assert len(result) == 1
        assert result[0] is play


class TestPlay:
    def test_play_result(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.result.type == "atBat"
        assert play.result.event == "Flyout"
        assert play.result.event_type == "field_out"
        assert "Bregman" in play.result.description
        assert play.result.is_out is True

    def test_play_about(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.about.at_bat_index == 0
        assert play.about.half_inning == "top"
        assert play.about.is_top_inning is True
        assert play.about.inning == 1
        assert play.about.is_complete is True

    def test_play_count(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.count.balls == 1
        assert play.count.strikes == 1
        assert play.count.outs == 1

    def test_scoring_play_result(self):
        """Verify a home run scoring play has correct scores."""
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        scoring_idx = resp.live_data.plays.scoring_plays[0]
        play = resp.live_data.plays.all_plays[scoring_idx]
        assert play.result.event == "Home Run"
        assert play.result.rbi >= 1
        assert play.about.is_scoring_play is True


class TestPlayPitchesProperty:
    """Tests for Play.pitches property."""

    def test_pitches_from_fixture(self):
        """play[0] has pitchIndex [4, 5, 6] and 7 playEvents."""
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]

        assert play.pitch_index == [4, 5, 6]
        pitches = play.pitches
        assert len(pitches) == 3
        # Each resolved event should be a pitch
        for p in pitches:
            assert p.is_pitch is True

    def test_pitches_match_play_events(self):
        """Resolved pitches should be the same objects as play_events[i]."""
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]

        for idx, pitch in zip(play.pitch_index, play.pitches):
            assert pitch is play.play_events[idx]

    def test_pitches_empty(self):
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            pitch_index=[],
            play_events=[],
        )
        assert play.pitches == []

    def test_pitches_skips_out_of_range(self):
        event = PlayEvent(is_pitch=True, index=0)
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            pitch_index=[0, 10],  # 10 is out of range
            play_events=[event],
        )
        assert len(play.pitches) == 1
        assert play.pitches[0] is event


class TestPlayActionsProperty:
    """Tests for Play.actions property."""

    def test_actions_from_fixture(self):
        """play[0] has actionIndex [0, 1, 2, 3] and 7 playEvents."""
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]

        assert play.action_index == [0, 1, 2, 3]
        actions = play.actions
        assert len(actions) == 4
        # Each resolved event should be an action
        for a in actions:
            assert a.type == "action"

    def test_actions_match_play_events(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]

        for idx, action in zip(play.action_index, play.actions):
            assert action is play.play_events[idx]

    def test_actions_empty(self):
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            action_index=[],
            play_events=[],
        )
        assert play.actions == []

    def test_actions_skips_out_of_range(self):
        event = PlayEvent(type="action", index=0)
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            action_index=[0, 99],
            play_events=[event],
        )
        assert len(play.actions) == 1


class TestPlayIndexedRunnersProperty:
    """Tests for Play.indexed_runners property."""

    def test_indexed_runners_from_fixture(self):
        """play[0] has runnerIndex [0] and 1 runner."""
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]

        assert play.runner_index == [0]
        indexed = play.indexed_runners
        assert len(indexed) == 1
        assert indexed[0] is play.runners[0]

    def test_indexed_runners_empty(self):
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            runner_index=[],
            runners=[],
        )
        assert play.indexed_runners == []

    def test_indexed_runners_skips_out_of_range(self):
        runner = Runner(movement=RunnerMovement(is_out=False))
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            runner_index=[0, 5],
            runners=[runner],
        )
        result = play.indexed_runners
        assert len(result) == 1
        assert result[0] is runner

    def test_indexed_runners_preserves_order(self):
        r0 = Runner(movement=RunnerMovement(origin_base="1B"))
        r1 = Runner(movement=RunnerMovement(origin_base="2B"))
        r2 = Runner(movement=RunnerMovement(origin_base="3B"))
        ref = PersonRef(id=1)
        play = Play(
            matchup=Matchup(batter=ref, pitcher=ref),
            runner_index=[2, 0],
            runners=[r0, r1, r2],
        )
        result = play.indexed_runners
        assert len(result) == 2
        assert result[0].movement.origin_base == "3B"
        assert result[1].movement.origin_base == "1B"


class TestPlayEventIsAction:
    """Tests for PlayEvent.is_action property."""

    def test_is_action_true(self):
        event = PlayEvent(type="action")
        assert event.is_action is True

    def test_is_action_false_for_pitch(self):
        event = PlayEvent(type="pitch")
        assert event.is_action is False

    def test_is_action_false_for_none(self):
        event = PlayEvent(type=None)
        assert event.is_action is False

    def test_is_action_from_fixture(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]

        action_events = [e for e in play.play_events if e.is_action]
        pitch_events = [e for e in play.play_events if e.is_pitch]
        assert len(action_events) > 0
        assert len(pitch_events) > 0
        # No event is both an action and a pitch
        for e in play.play_events:
            if e.is_action:
                assert e.is_pitch is not True


class TestMatchup:
    def test_batter_pitcher(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.matchup.batter.full_name == "Alex Bregman"
        assert play.matchup.pitcher.full_name == "Yariel Rodríguez"

    def test_handedness(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.matchup.bat_side.code == "R"
        assert play.matchup.pitch_hand.code == "R"

    def test_splits(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert play.matchup.splits.batter == "vs_RHP"
        assert play.matchup.splits.pitcher == "vs_RHB"
        assert play.matchup.splits.men_on_base == "Empty"


class TestPlayEvents:
    def test_pitch_event(self):
        """Verify a pitch event has full pitch data."""
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
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        pitches = [e for e in play.play_events if e.is_pitch]
        pitch = pitches[0]
        assert pitch.pitch_data.start_speed == 95.9
        assert pitch.pitch_data.end_speed == 89.0

    def test_pitch_data_coordinates(self):
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
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        pitches = [e for e in play.play_events if e.is_pitch]
        breaks = pitches[0].pitch_data.breaks
        assert breaks.spin_rate == 2191
        assert breaks.spin_direction == 217
        assert breaks.break_vertical is not None

    def test_pitch_type(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        pitches = [e for e in play.play_events if e.is_pitch]
        assert pitches[0].details.type.code == "FF"
        assert pitches[0].details.type.description == "Four-Seam Fastball"

    def test_action_event(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        actions = [e for e in play.play_events if not e.is_pitch]
        assert len(actions) > 0
        assert actions[0].is_action is True

    def test_play_events_unknown_handling(self):
        data = load_fixture("malformed_play_events")
        play = Play.model_validate(data)

        for event in play.play_events:
            assert event.details.type.code is not None
            if event.details.type.description.lower() == "unknown":
                assert event.details.type.code == PitchTypeEnum.UNKNOWN


class TestRunners:
    def test_runner_movement(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        assert len(play.runners) > 0
        runner = play.runners[0]
        assert runner.movement.is_out is True
        assert runner.movement.out_base == "1B"
        assert runner.movement.out_number == 1

    def test_runner_details(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        runner = play.runners[0]
        assert runner.details.event == "Flyout"
        assert runner.details.runner.full_name == "Alex Bregman"
        assert runner.details.is_scoring_event is False

    def test_fielding_credits(self):
        data = load_fixture("livefeed")
        resp = LiveFeedResponse.model_validate(data)
        play = resp.live_data.plays.all_plays[0]
        runner = play.runners[0]
        assert len(runner.credits) > 0
        credit = runner.credits[0]
        assert credit.credit == "f_putout"
        assert credit.position.abbreviation == "CF"
