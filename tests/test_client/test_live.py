"""Tests for the live game client."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from mlb_statsapi.client.live import (
    FetchGranularity,
    GameEvent,
    GameEventData,
    LiveGameClient,
    LiveGameConfig,
    SyncLiveGameClient,
    _detect_events,
    _should_fetch,
)
from mlb_statsapi.models.livefeed import LiveFeedResponse
from mlb_statsapi.models.ws import WsMessage

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_feed() -> LiveFeedResponse:
    data = json.loads((FIXTURES_DIR / "livefeed.json").read_text())
    return LiveFeedResponse.model_validate(data)


def _make_ws_message(**overrides: object) -> WsMessage:
    defaults: dict[str, object] = {
        "timeStamp": "20240605_200600",
        "gamePk": "744914",
        "updateId": "test-id",
        "wait": 10,
        "logicalEvents": [],
        "gameEvents": [],
    }
    defaults.update(overrides)
    return WsMessage.model_validate(defaults)


# ---------------------------------------------------------------------------
# WsMessage model
# ---------------------------------------------------------------------------


class TestWsMessage:
    def test_parse_minimal(self) -> None:
        msg = WsMessage.model_validate(
            {"timeStamp": "20230721_182018", "gamePk": "717325"}
        )
        assert msg.time_stamp == "20230721_182018"
        assert msg.game_pk == "717325"
        assert msg.wait == 10
        assert msg.game_events == []
        assert msg.logical_events == []

    def test_parse_full(self) -> None:
        msg = WsMessage.model_validate(
            {
                "timeStamp": "20230721_182018",
                "gamePk": "717325",
                "updateId": "7a5b0181-f833-4de8-bf1b-65de5e3ef6a3",
                "wait": 10,
                "logicalEvents": ["countChange", "count10", "basesEmpty"],
                "gameEvents": ["ball"],
                "changeEvent": {"type": "new_entry"},
            }
        )
        assert msg.update_id == "7a5b0181-f833-4de8-bf1b-65de5e3ef6a3"
        assert "countChange" in msg.logical_events
        assert "ball" in msg.game_events
        assert msg.change_event is not None
        assert msg.change_event.type == "new_entry"

    def test_unknown_events_accepted(self) -> None:
        """Unknown event values should be accepted via | str."""
        msg = WsMessage.model_validate(
            {
                "timeStamp": "20230721_182018",
                "gamePk": "717325",
                "gameEvents": ["someFutureEvent"],
                "logicalEvents": ["unknownLogical"],
            }
        )
        assert "someFutureEvent" in msg.game_events
        assert "unknownLogical" in msg.logical_events


# ---------------------------------------------------------------------------
# Granularity filter
# ---------------------------------------------------------------------------


class TestGranularityFilter:
    def test_every_update_always_fetches(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.EVERY_UPDATE)
        msg = _make_ws_message(gameEvents=[])
        assert _should_fetch(msg, config) is True

    def test_every_pitch_fetches_on_ball(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.EVERY_PITCH)
        msg = _make_ws_message(gameEvents=["ball"])
        assert _should_fetch(msg, config) is True

    def test_every_pitch_fetches_on_called_strike(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.EVERY_PITCH)
        msg = _make_ws_message(gameEvents=["called_strike"])
        assert _should_fetch(msg, config) is True

    def test_every_pitch_skips_non_pitch(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.EVERY_PITCH)
        msg = _make_ws_message(gameEvents=["game_advisory"])
        assert _should_fetch(msg, config) is False

    def test_every_play_fetches_on_field_out(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.EVERY_PLAY)
        msg = _make_ws_message(gameEvents=["field_out"])
        assert _should_fetch(msg, config) is True

    def test_every_play_skips_ball(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.EVERY_PLAY)
        msg = _make_ws_message(gameEvents=["ball"])
        assert _should_fetch(msg, config) is False

    def test_scoring_only_fetches_on_hit_into_play_score(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.SCORING_ONLY)
        msg = _make_ws_message(gameEvents=["hit_into_play_score"])
        assert _should_fetch(msg, config) is True

    def test_scoring_only_skips_strikeout(self) -> None:
        config = LiveGameConfig(granularity=FetchGranularity.SCORING_ONLY)
        msg = _make_ws_message(gameEvents=["strikeout"])
        assert _should_fetch(msg, config) is False

    def test_custom_triggers_game_events(self) -> None:
        config = LiveGameConfig(
            granularity=FetchGranularity.CUSTOM,
            custom_triggers=["caught_stealing_2b"],
        )
        msg = _make_ws_message(gameEvents=["caught_stealing_2b"])
        assert _should_fetch(msg, config) is True

    def test_custom_triggers_logical_events(self) -> None:
        config = LiveGameConfig(
            granularity=FetchGranularity.CUSTOM,
            custom_triggers=["basesLoaded"],
        )
        msg = _make_ws_message(logicalEvents=["basesLoaded"])
        assert _should_fetch(msg, config) is True

    def test_custom_triggers_no_match(self) -> None:
        config = LiveGameConfig(
            granularity=FetchGranularity.CUSTOM,
            custom_triggers=["caught_stealing_2b"],
        )
        msg = _make_ws_message(gameEvents=["ball"])
        assert _should_fetch(msg, config) is False


# ---------------------------------------------------------------------------
# Event detection
# ---------------------------------------------------------------------------


class TestEventDetection:
    def test_first_feed_emits_update(self) -> None:
        feed = _load_feed()
        events = _detect_events(None, feed)
        types = {e.event_type for e in events}
        assert GameEvent.UPDATE in types

    def test_game_state_change_detected(self) -> None:
        old = _load_feed()
        new = _load_feed()
        # Modify old to be "Live" so transition to "Final" is detected
        assert old.game_data.status is not None
        old.game_data.status.abstract_game_state = "Live"
        events = _detect_events(old, new)
        types = {str(e.event_type) for e in events}
        assert str(GameEvent.GAME_STATE_CHANGE) in types
        assert str(GameEvent.GAME_END) in types

    def test_game_start_detected(self) -> None:
        old = _load_feed()
        new = _load_feed()
        assert old.game_data.status is not None
        assert new.game_data.status is not None
        old.game_data.status.abstract_game_state = "Preview"
        new.game_data.status.abstract_game_state = "Live"
        events = _detect_events(old, new)
        types = {str(e.event_type) for e in events}
        assert str(GameEvent.GAME_START) in types

    def test_new_play_detected(self) -> None:
        old = _load_feed()
        new = _load_feed()
        assert new.live_data.plays is not None
        assert old.live_data.plays is not None
        # Remove last play from old to simulate new play appearing
        old.live_data.plays.all_plays = old.live_data.plays.all_plays[:-1]
        events = _detect_events(old, new)
        types = {str(e.event_type) for e in events}
        assert str(GameEvent.PLAY_COMPLETE) in types

    def test_new_pitch_detected(self) -> None:
        old = _load_feed()
        new = _load_feed()
        assert new.live_data.plays is not None
        assert new.live_data.plays.current_play is not None
        assert old.live_data.plays is not None
        assert old.live_data.plays.current_play is not None
        # Remove last pitch from old's current play
        if len(old.live_data.plays.current_play.play_events) > 1:
            old.live_data.plays.current_play.play_events = (
                old.live_data.plays.current_play.play_events[:-1]
            )
            events = _detect_events(old, new)
            types = {str(e.event_type) for e in events}
            assert str(GameEvent.PITCH) in types

    def test_inning_change_detected(self) -> None:
        old = _load_feed()
        new = _load_feed()
        assert old.live_data.linescore is not None
        assert new.live_data.linescore is not None
        old.live_data.linescore.current_inning = 8
        new.live_data.linescore.current_inning = 9
        events = _detect_events(old, new)
        types = {str(e.event_type) for e in events}
        assert str(GameEvent.INNING_CHANGE) in types

    def test_half_inning_change_detected(self) -> None:
        old = _load_feed()
        new = _load_feed()
        assert old.live_data.linescore is not None
        assert new.live_data.linescore is not None
        old.live_data.linescore.inning_half = "Top"
        new.live_data.linescore.inning_half = "Bottom"
        events = _detect_events(old, new)
        types = {str(e.event_type) for e in events}
        assert str(GameEvent.INNING_CHANGE) in types

    def test_run_scored_detected(self) -> None:
        old = _load_feed()
        new = _load_feed()
        assert old.live_data.linescore is not None
        assert old.live_data.linescore.teams is not None
        # Reduce old score so new score looks like a run was scored
        old.live_data.linescore.teams.home.runs = 0
        events = _detect_events(old, new)
        types = {str(e.event_type) for e in events}
        assert str(GameEvent.RUN) in types

    def test_no_change_emits_only_update(self) -> None:
        feed = _load_feed()
        events = _detect_events(feed, feed)
        # Same object — no state changes detected beyond UPDATE
        types = {str(e.event_type) for e in events}
        assert str(GameEvent.UPDATE) in types
        assert str(GameEvent.GAME_STATE_CHANGE) not in types
        assert str(GameEvent.PLAY_COMPLETE) not in types
        assert str(GameEvent.INNING_CHANGE) not in types
        assert str(GameEvent.RUN) not in types

    def test_event_data_carries_timecodes(self) -> None:
        feed = _load_feed()
        events = _detect_events(
            None,
            feed,
            start_timecode="20240605_200000",
            end_timecode="20240605_200600",
        )
        assert events[0].start_timecode == "20240605_200000"
        assert events[0].end_timecode == "20240605_200600"

    def test_event_data_carries_ws_message(self) -> None:
        feed = _load_feed()
        msg = _make_ws_message(gameEvents=["ball"])
        events = _detect_events(None, feed, ws_message=msg)
        assert events[0].ws_message is msg

    def test_event_data_carries_diff(self) -> None:
        feed = _load_feed()
        diff_feed = _load_feed()
        events = _detect_events(None, feed, diff=diff_feed)
        assert events[0].diff is diff_feed


# ---------------------------------------------------------------------------
# LiveGameClient
# ---------------------------------------------------------------------------


class TestLiveGameClient:
    def test_callback_registration(self) -> None:
        client = LiveGameClient(game_pk=744914)

        called = []

        @client.on(GameEvent.PITCH)
        async def handler(event: GameEventData) -> None:
            called.append(event)

        assert str(GameEvent.PITCH) in client._handlers
        assert len(client._handlers[str(GameEvent.PITCH)]) == 1

    def test_multi_event_registration(self) -> None:
        client = LiveGameClient(game_pk=744914)

        @client.on([GameEvent.PITCH, GameEvent.HIT])
        async def handler(event: GameEventData) -> None:
            pass

        assert str(GameEvent.PITCH) in client._handlers
        assert str(GameEvent.HIT) in client._handlers

    def test_direct_handler_registration(self) -> None:
        client = LiveGameClient(game_pk=744914)

        async def handler(event: GameEventData) -> None:
            pass

        client.on(GameEvent.RUN, handler=handler)
        assert len(client._handlers[str(GameEvent.RUN)]) == 1

    def test_properties(self) -> None:
        client = LiveGameClient(game_pk=744914)
        assert client.game_pk == 744914
        assert client.feed is None
        assert client.is_running is False

    @pytest.mark.asyncio
    async def test_dispatch_fires_callbacks(self) -> None:
        client = LiveGameClient(game_pk=744914)
        received: list[GameEventData] = []

        @client.on(GameEvent.UPDATE)
        async def handler(event: GameEventData) -> None:
            received.append(event)

        event = GameEventData(
            event_type=GameEvent.UPDATE,
            game_pk=744914,
        )
        await client._dispatch(event)
        assert len(received) == 1
        assert received[0].event_type == GameEvent.UPDATE

    @pytest.mark.asyncio
    async def test_dispatch_pushes_to_stream_queue(self) -> None:
        client = LiveGameClient(game_pk=744914)
        queue: asyncio.Queue[GameEventData | None] = asyncio.Queue()
        client._queues.append(({str(GameEvent.PITCH)}, queue))

        # Should be pushed (matches filter)
        pitch_event = GameEventData(event_type=GameEvent.PITCH, game_pk=744914)
        await client._dispatch(pitch_event)
        assert not queue.empty()
        item = await queue.get()
        assert item is not None
        assert item.event_type == GameEvent.PITCH

        # Should NOT be pushed (doesn't match filter)
        run_event = GameEventData(event_type=GameEvent.RUN, game_pk=744914)
        await client._dispatch(run_event)
        assert queue.empty()

    @pytest.mark.asyncio
    async def test_dispatch_no_filter_gets_all(self) -> None:
        client = LiveGameClient(game_pk=744914)
        queue: asyncio.Queue[GameEventData | None] = asyncio.Queue()
        client._queues.append((None, queue))  # None = no filter

        event = GameEventData(event_type=GameEvent.SUBSTITUTION, game_pk=744914)
        await client._dispatch(event)
        assert not queue.empty()

    @pytest.mark.asyncio
    async def test_handler_error_does_not_crash(self) -> None:
        client = LiveGameClient(game_pk=744914)

        @client.on(GameEvent.UPDATE)
        async def bad_handler(event: GameEventData) -> None:
            raise ValueError("boom")

        event = GameEventData(event_type=GameEvent.UPDATE, game_pk=744914)
        # Should not raise
        await client._dispatch(event)

    @pytest.mark.asyncio
    async def test_is_game_over(self) -> None:
        feed = _load_feed()
        assert LiveGameClient._is_game_over(feed) is True

        assert feed.game_data.status is not None
        feed.game_data.status.abstract_game_state = "Live"
        assert LiveGameClient._is_game_over(feed) is False

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        async with LiveGameClient(game_pk=744914) as client:
            assert client.game_pk == 744914


# ---------------------------------------------------------------------------
# SyncLiveGameClient
# ---------------------------------------------------------------------------


class TestSyncLiveGameClient:
    def test_callback_registration(self) -> None:
        client = SyncLiveGameClient(game_pk=744914)

        @client.on(GameEvent.PITCH)
        def handler(event: GameEventData) -> None:
            pass

        assert str(GameEvent.PITCH) in client._sync_handlers

    def test_properties(self) -> None:
        client = SyncLiveGameClient(game_pk=744914)
        assert client.game_pk == 744914
        assert client.feed is None

    def test_context_manager(self) -> None:
        with SyncLiveGameClient(game_pk=744914) as client:
            assert client.game_pk == 744914


# ---------------------------------------------------------------------------
# Config model
# ---------------------------------------------------------------------------


class TestLiveGameConfig:
    def test_defaults(self) -> None:
        config = LiveGameConfig()
        assert config.granularity == FetchGranularity.EVERY_PITCH
        assert config.poll_interval == 10.0
        assert config.fetch_diff is False
        assert config.use_rest_fallback is True

    def test_custom_config(self) -> None:
        config = LiveGameConfig(
            granularity=FetchGranularity.SCORING_ONLY,
            fetch_diff=True,
            poll_interval=5.0,
        )
        assert config.granularity == FetchGranularity.SCORING_ONLY
        assert config.fetch_diff is True
        assert config.poll_interval == 5.0
