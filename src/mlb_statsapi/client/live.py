"""Live game client with WebSocket push notifications and REST enrichment.

Provides :class:`LiveGameClient` (async) and :class:`SyncLiveGameClient`
(sync) for watching MLB games in real time. The client connects to the
undocumented MLB gameday WebSocket at
``wss://ws.statsapi.mlb.com/api/v1/game/push/subscribe/gameday/<gamePk>``
to receive lightweight push notifications, then optionally fetches full
game data via REST based on user-configured granularity.

Usage (async)::

    async with LiveGameClient(game_pk=824782) as client:

        @client.on(GameEvent.PITCH)
        async def on_pitch(event: GameEventData):
            pe = event.play_event
            if pe and pe.details:
                print(f"Pitch: {pe.details.description}")

        await client.watch()

Usage (sync)::

    with SyncLiveGameClient(game_pk=824782) as client:

        @client.on(GameEvent.PITCH)
        def on_pitch(event: GameEventData):
            pe = event.play_event
            if pe and pe.details:
                print(f"Pitch: {pe.details.description}")

        client.watch()
"""

from __future__ import annotations

import asyncio
import logging
import sys
import threading
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from typing import Any

import httpx

from mlb_statsapi.client.async_client import AsyncMlbClient
from mlb_statsapi.exceptions import MlbApiError
from mlb_statsapi.models._base import MlbBaseModel
from mlb_statsapi.models.enums import AbstractGameState, EventType
from mlb_statsapi.models.livefeed import LiveFeedResponse, Play, PlayEvent
from mlb_statsapi.models.ws import WsGameEvent, WsMessage

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport of StrEnum for Python < 3.11."""


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums and configuration
# ---------------------------------------------------------------------------


class GameEvent(StrEnum):
    """Client-side events detected after comparing game states.

    These events are emitted by :class:`LiveGameClient` when changes
    are detected in the live feed data.
    """

    WS_MESSAGE = "ws_message"
    UPDATE = "update"
    GAME_START = "game_start"
    GAME_END = "game_end"
    GAME_STATE_CHANGE = "game_state_change"
    PITCH = "pitch"
    HIT = "hit"
    PLAY_COMPLETE = "play_complete"
    STRIKEOUT = "strikeout"
    WALK = "walk"
    HOME_RUN = "home_run"
    RUN = "run"
    INNING_CHANGE = "inning_change"
    SUBSTITUTION = "substitution"


class FetchGranularity(StrEnum):
    """Preset granularity levels controlling when WS notifications trigger
    a REST fetch for full game data.
    """

    EVERY_UPDATE = "every_update"
    EVERY_PITCH = "every_pitch"
    EVERY_PLAY = "every_play"
    SCORING_ONLY = "scoring_only"
    CUSTOM = "custom"


class LiveGameConfig(MlbBaseModel):
    """Configuration for :class:`LiveGameClient`."""

    # WebSocket
    ws_url_template: str = (
        "wss://ws.statsapi.mlb.com/api/v1/game/push/subscribe/gameday/{game_pk}"
    )
    ws_reconnect_delay: float = 2.0
    ws_max_reconnect_delay: float = 60.0

    # Granularity — controls when WS notifications trigger REST fetches
    granularity: FetchGranularity | str = FetchGranularity.EVERY_PITCH
    custom_triggers: list[str] = []

    # Enrichment
    fetch_diff: bool = False

    # REST polling fallback
    poll_interval: float = 10.0
    pregame_poll_interval: float = 60.0
    use_rest_fallback: bool = True

    # Lifecycle
    postgame_linger: float = 0.0
    max_retries: int = 5
    retry_delay: float = 5.0


# ---------------------------------------------------------------------------
# Event data model
# ---------------------------------------------------------------------------


class GameEventData(MlbBaseModel):
    """Payload delivered to callbacks and stream consumers."""

    event_type: GameEvent | str
    game_pk: int
    ws_message: WsMessage | None = None
    feed: LiveFeedResponse | None = None
    previous_feed: LiveFeedResponse | None = None
    play: Play | None = None
    play_event: PlayEvent | None = None
    start_timecode: str = ""
    end_timecode: str = ""
    diff: LiveFeedResponse | None = None


# ---------------------------------------------------------------------------
# Granularity filter
# ---------------------------------------------------------------------------

# Mapping from FetchGranularity presets to the WS gameEvent values that
# should trigger a REST fetch.
_PITCH_TRIGGERS: frozenset[str] = frozenset(
    {
        # Pitch results
        WsGameEvent.BALL,
        WsGameEvent.CALLED_STRIKE,
        WsGameEvent.SWINGING_STRIKE,
        WsGameEvent.FOUL,
        WsGameEvent.FOUL_TIP,
        WsGameEvent.FOUL_BUNT,
        WsGameEvent.BLOCKED_BALL,
        WsGameEvent.HIT_INTO_PLAY,
        WsGameEvent.HIT_INTO_PLAY_NO_OUT,
        WsGameEvent.HIT_INTO_PLAY_SCORE,
        # Play outcomes
        WsGameEvent.SINGLE,
        WsGameEvent.DOUBLE,
        WsGameEvent.TRIPLE,
        WsGameEvent.FIELD_OUT,
        WsGameEvent.STRIKEOUT,
        WsGameEvent.WALK,
        WsGameEvent.FORCE_OUT,
        WsGameEvent.SAC_FLY,
        WsGameEvent.GROUNDED_INTO_DOUBLE_PLAY,
        WsGameEvent.CAUGHT_STEALING_2B,
    }
)

_PLAY_TRIGGERS: frozenset[str] = frozenset(
    {
        # Play completion events
        WsGameEvent.SINGLE,
        WsGameEvent.DOUBLE,
        WsGameEvent.TRIPLE,
        WsGameEvent.FIELD_OUT,
        WsGameEvent.STRIKEOUT,
        WsGameEvent.WALK,
        WsGameEvent.FORCE_OUT,
        WsGameEvent.SAC_FLY,
        WsGameEvent.GROUNDED_INTO_DOUBLE_PLAY,
        WsGameEvent.CAUGHT_STEALING_2B,
        # Substitutions
        WsGameEvent.PITCHING_SUBSTITUTION,
        WsGameEvent.OFFENSIVE_SUBSTITUTION,
        WsGameEvent.DEFENSIVE_SWITCH,
    }
)

_SCORING_TRIGGERS: frozenset[str] = frozenset(
    {
        WsGameEvent.HIT_INTO_PLAY_SCORE,
    }
)


def _should_fetch(msg: WsMessage, config: LiveGameConfig) -> bool:
    """Return True if *msg* should trigger a REST fetch given *config*."""
    granularity = config.granularity
    events = set(msg.game_events)

    if granularity == FetchGranularity.EVERY_UPDATE:
        return True
    if granularity == FetchGranularity.EVERY_PITCH:
        return bool(events & _PITCH_TRIGGERS)
    if granularity == FetchGranularity.EVERY_PLAY:
        return bool(events & _PLAY_TRIGGERS)
    if granularity == FetchGranularity.SCORING_ONLY:
        return bool(events & _SCORING_TRIGGERS)
    if granularity == FetchGranularity.CUSTOM:
        custom = set(config.custom_triggers)
        return bool(events & custom) or bool(set(msg.logical_events) & custom)
    # Unknown granularity — fetch to be safe
    return True


# ---------------------------------------------------------------------------
# Event detection
# ---------------------------------------------------------------------------

# Event types that indicate a strikeout
_STRIKEOUT_EVENTS: frozenset[str] = frozenset(
    {
        EventType.STRIKEOUT,
        EventType.STRIKE_OUT,
        EventType.STRIKEOUT_DOUBLE_PLAY,
        EventType.STRIKEOUT_TRIPLE_PLAY,
    }
)

_WALK_EVENTS: frozenset[str] = frozenset(
    {
        EventType.WALK,
        EventType.INTENT_WALK,
    }
)


def _detect_events(
    old: LiveFeedResponse | None,
    new: LiveFeedResponse,
    *,
    ws_message: WsMessage | None = None,
    start_timecode: str = "",
    end_timecode: str = "",
    diff: LiveFeedResponse | None = None,
) -> list[GameEventData]:
    """Compare two feed states and return all detected events."""
    events: list[GameEventData] = []
    game_pk = int(new.game_pk)

    def _make(
        event_type: GameEvent,
        *,
        play: Play | None = None,
        play_event: PlayEvent | None = None,
    ) -> GameEventData:
        return GameEventData(
            event_type=event_type,
            game_pk=game_pk,
            ws_message=ws_message,
            feed=new,
            previous_feed=old,
            play=play,
            play_event=play_event,
            start_timecode=start_timecode,
            end_timecode=end_timecode,
            diff=diff,
        )

    # Always emit UPDATE
    events.append(_make(GameEvent.UPDATE))

    # --- Game state changes ---
    old_state = (
        old.game_data.status.abstract_game_state
        if old and old.game_data and old.game_data.status
        else None
    )
    new_state = (
        new.game_data.status.abstract_game_state
        if new.game_data and new.game_data.status
        else None
    )

    if old_state and new_state and old_state != new_state:
        events.append(_make(GameEvent.GAME_STATE_CHANGE))
        if new_state == AbstractGameState.LIVE:
            events.append(_make(GameEvent.GAME_START))
        elif new_state == AbstractGameState.FINAL:
            events.append(_make(GameEvent.GAME_END))

    new_plays = new.live_data.plays if new.live_data else None
    old_plays = old.live_data.plays if old and old.live_data else None

    # --- New completed plays ---
    new_all = new_plays.all_plays if new_plays else []
    old_all_len = len(old_plays.all_plays) if old_plays else 0

    for play in new_all[old_all_len:]:
        events.append(_make(GameEvent.PLAY_COMPLETE, play=play))

        event_type = play.result.event_type if play.result else None
        if event_type:
            if event_type in _STRIKEOUT_EVENTS:
                events.append(_make(GameEvent.STRIKEOUT, play=play))
            elif event_type in _WALK_EVENTS:
                events.append(_make(GameEvent.WALK, play=play))
            elif event_type == EventType.HOME_RUN:
                events.append(_make(GameEvent.HOME_RUN, play=play))

    # --- New pitches in current play ---
    new_current = new_plays.current_play if new_plays else None
    old_current = old_plays.current_play if old_plays else None

    new_events_list = new_current.play_events if new_current else []
    old_events_len = len(old_current.play_events) if old_current else 0

    # If the current play changed (new at-bat), treat all events as new
    new_at_bat_idx = new_current.at_bat_index if new_current else None
    old_at_bat_idx = old_current.at_bat_index if old_current else None
    if new_at_bat_idx != old_at_bat_idx:
        old_events_len = 0

    for pe in new_events_list[old_events_len:]:
        if pe.is_pitch:
            events.append(_make(GameEvent.PITCH, play=new_current, play_event=pe))
            if pe.details and pe.details.is_in_play:
                events.append(_make(GameEvent.HIT, play=new_current, play_event=pe))
        elif pe.is_substitution:
            events.append(
                _make(GameEvent.SUBSTITUTION, play=new_current, play_event=pe)
            )

    # --- Inning changes ---
    new_ls = new.live_data.linescore if new.live_data else None
    old_ls = old.live_data.linescore if old and old.live_data else None

    if new_ls and old_ls:
        inning_changed = new_ls.current_inning != old_ls.current_inning
        half_changed = new_ls.inning_half != old_ls.inning_half
        if inning_changed or half_changed:
            events.append(_make(GameEvent.INNING_CHANGE))

    # --- Run scored ---
    if new_ls and old_ls and new_ls.teams and old_ls.teams:
        new_home_runs = new_ls.teams.home.runs or 0
        old_home_runs = old_ls.teams.home.runs or 0
        new_away_runs = new_ls.teams.away.runs or 0
        old_away_runs = old_ls.teams.away.runs or 0
        if new_home_runs > old_home_runs or new_away_runs > old_away_runs:
            events.append(_make(GameEvent.RUN))

    return events


# ---------------------------------------------------------------------------
# WebSocket connection
# ---------------------------------------------------------------------------


async def _ws_receive(
    game_pk: int,
    config: LiveGameConfig,
    stop_event: asyncio.Event,
) -> AsyncIterator[WsMessage]:
    """Connect to the gameday WebSocket and yield parsed messages.

    Reconnects with exponential backoff on disconnection.
    """
    from httpx_ws import aconnect_ws

    url = config.ws_url_template.format(game_pk=game_pk)
    delay = config.ws_reconnect_delay

    while not stop_event.is_set():
        try:
            async with aconnect_ws(url, keepalive_ping_interval_seconds=20) as ws:  # type: ignore[var-annotated]
                delay = config.ws_reconnect_delay  # reset on success
                logger.info("WebSocket connected for game %s", game_pk)
                while not stop_event.is_set():
                    try:
                        raw = await asyncio.wait_for(ws.receive_text(), timeout=120)
                    except asyncio.TimeoutError:
                        # No message in 120s — keep alive, loop back
                        continue
                    try:
                        msg = WsMessage.model_validate_json(raw)
                    except Exception:
                        logger.warning("Unrecognized WS message, skipping: %.200s", raw)
                        continue
                    logger.debug(
                        "WS message: gameEvents=%s logicalEvents=%s ts=%s",
                        msg.game_events,
                        msg.logical_events,
                        msg.time_stamp,
                    )
                    yield msg
        except Exception as exc:
            if stop_event.is_set():
                return
            logger.warning(
                "WebSocket disconnected (%s), reconnecting in %.1fs",
                exc,
                delay,
            )
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=delay)
                return  # stop was requested during backoff
            except asyncio.TimeoutError:
                pass
            delay = min(delay * 2, config.ws_max_reconnect_delay)


# ---------------------------------------------------------------------------
# REST polling fallback
# ---------------------------------------------------------------------------


async def _rest_poll(
    game_pk: int,
    api: AsyncMlbClient,
    config: LiveGameConfig,
    stop_event: asyncio.Event,
    last_feed: LiveFeedResponse | None,
) -> AsyncIterator[tuple[LiveFeedResponse, str]]:
    """Poll the REST API for game updates, yielding (feed, timecode) tuples.

    Uses the timestamps endpoint as a change-detection gate to avoid
    unnecessary full feed fetches.
    """
    last_timecode = ""

    while not stop_event.is_set():
        # Determine poll interval based on game state
        interval = config.poll_interval
        if last_feed and last_feed.game_data and last_feed.game_data.status:
            state = last_feed.game_data.status.abstract_game_state or ""
            if state == AbstractGameState.PREVIEW:
                interval = config.pregame_poll_interval
            elif state == AbstractGameState.FINAL:
                return

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
            return  # stop was requested
        except asyncio.TimeoutError:
            pass

        try:
            timestamps = await api.game_timestamps(game_pk)
            ts_list = timestamps.root if hasattr(timestamps, "root") else []
            current_timecode = ts_list[-1] if ts_list else ""

            if current_timecode and current_timecode == last_timecode:
                continue  # no change

            last_timecode = current_timecode
            logger.debug(
                "REST poll fetch for game %s (timecode=%s)",
                game_pk,
                current_timecode,
            )
            feed = await api.game(game_pk)
            last_feed = feed
            yield feed, current_timecode

        except (MlbApiError, httpx.HTTPError) as exc:
            logger.warning("REST poll error: %s", exc)
            continue


# ---------------------------------------------------------------------------
# LiveGameClient (async)
# ---------------------------------------------------------------------------

# Type alias for async and sync callback signatures
AsyncHandler = Callable[[GameEventData], Awaitable[None]]
SyncHandler = Callable[[GameEventData], Any]


class LiveGameClient:
    """Async live game client with WebSocket push and REST enrichment.

    Connects to the MLB gameday WebSocket for real-time push notifications,
    then optionally fetches full game data via REST based on the configured
    :class:`FetchGranularity`.

    Parameters
    ----------
    game_pk:
        The MLB game primary key to watch.
    client:
        Optional :class:`~mlb_statsapi.AsyncMlbClient` instance for REST
        calls. If not provided, one is created and managed internally.
    config:
        Optional :class:`LiveGameConfig`. Uses defaults if not provided.
    """

    def __init__(
        self,
        game_pk: int,
        *,
        client: AsyncMlbClient | None = None,
        config: LiveGameConfig | None = None,
    ) -> None:
        self._game_pk = game_pk
        self._config = config or LiveGameConfig()
        self._owns_client = client is None
        self._api = client or AsyncMlbClient()
        self._feed: LiveFeedResponse | None = None
        self._stop = asyncio.Event()
        self._running = False
        self._handlers: dict[str, list[AsyncHandler]] = {}
        self._queues: list[
            tuple[set[str] | None, asyncio.Queue[GameEventData | None]]
        ] = []
        self._last_timecode = ""

    @property
    def api(self) -> AsyncMlbClient:
        """The underlying REST client, exposed for enrichment requests."""
        return self._api

    @property
    def feed(self) -> LiveFeedResponse | None:
        """The most recent :class:`LiveFeedResponse`, or ``None``."""
        return self._feed

    @property
    def is_running(self) -> bool:
        """Whether :meth:`watch` is currently active."""
        return self._running

    @property
    def game_pk(self) -> int:
        """The game primary key being watched."""
        return self._game_pk

    # -- Callback registration --

    def on(
        self,
        event_type: GameEvent | str | Sequence[GameEvent | str],
        handler: AsyncHandler | None = None,
    ) -> Callable[[AsyncHandler], AsyncHandler]:
        """Register a callback for one or more event types.

        Can be used as a decorator::

            @client.on(GameEvent.PITCH)
            async def on_pitch(event: GameEventData): ...

        Or called directly::

            client.on(GameEvent.PITCH, handler=my_handler)
        """
        types = [event_type] if isinstance(event_type, str) else list(event_type)

        def _register(fn: AsyncHandler) -> AsyncHandler:
            for t in types:
                self._handlers.setdefault(str(t), []).append(fn)
            return fn

        if handler is not None:
            _register(handler)
            return _register
        return _register

    # -- Async iterator --

    async def stream(
        self, *event_types: GameEvent | str
    ) -> AsyncIterator[GameEventData]:
        """Async iterator yielding :class:`GameEventData` for selected events.

        If no event types are specified, all events are yielded.

        Usage::

            async for event in client.stream(GameEvent.PITCH, GameEvent.RUN):
                print(event.event_type)

        .. note::
            Call :meth:`watch` concurrently (e.g. via ``asyncio.create_task``)
            to drive the event loop.
        """
        filter_set: set[str] | None = (
            {str(t) for t in event_types} if event_types else None
        )
        queue: asyncio.Queue[GameEventData | None] = asyncio.Queue()
        entry = (filter_set, queue)
        self._queues.append(entry)
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item
        finally:
            if entry in self._queues:
                self._queues.remove(entry)

    # -- Lifecycle --

    async def watch(self) -> None:
        """Watch the game until it ends or :meth:`stop` is called.

        Connects to the WebSocket for push notifications. If the
        WebSocket is unavailable and ``use_rest_fallback`` is enabled,
        falls back to REST polling.
        """
        self._running = True
        self._stop.clear()
        try:
            # Fetch initial state via REST
            await self._fetch_initial()
            # Try WebSocket first
            try:
                await self._watch_ws()
            except Exception as exc:
                if self._stop.is_set():
                    return
                logger.warning("WebSocket failed (%s)", exc)
                if self._config.use_rest_fallback:
                    logger.info(
                        "Falling back to REST polling for game %s", self._game_pk
                    )
                    await self._watch_rest()
                else:
                    raise
        finally:
            self._running = False
            # Signal stream consumers to stop
            for _, queue in self._queues:
                await queue.put(None)

    async def stop(self) -> None:
        """Signal the watch loop to stop."""
        self._stop.set()

    async def close(self) -> None:
        """Stop watching and release resources."""
        await self.stop()
        if self._owns_client:
            await self._api.close()

    async def __aenter__(self) -> LiveGameClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    # -- Internal: initial fetch --

    async def _fetch_initial(self) -> None:
        """Fetch the initial game state via REST."""
        retries = 0
        while not self._stop.is_set():
            try:
                self._feed = await self._api.game(self._game_pk)
                return
            except (MlbApiError, httpx.HTTPError) as exc:
                retries += 1
                if retries > self._config.max_retries:
                    raise
                logger.warning(
                    "Initial fetch failed (%s), retry %d/%d",
                    exc,
                    retries,
                    self._config.max_retries,
                )
                try:
                    await asyncio.wait_for(
                        self._stop.wait(), timeout=self._config.retry_delay
                    )
                    return
                except asyncio.TimeoutError:
                    pass

    # -- Internal: WebSocket watch loop --

    async def _watch_ws(self) -> None:
        """Main watch loop using WebSocket push notifications."""
        async for msg in _ws_receive(self._game_pk, self._config, self._stop):
            if self._stop.is_set():
                return

            # Always emit raw WS_MESSAGE event
            ws_event = GameEventData(
                event_type=GameEvent.WS_MESSAGE,
                game_pk=self._game_pk,
                ws_message=msg,
                feed=self._feed,
                end_timecode=msg.time_stamp,
                start_timecode=self._last_timecode,
            )
            await self._dispatch(ws_event)

            # Check if we should fetch full game data
            if not _should_fetch(msg, self._config):
                self._last_timecode = msg.time_stamp
                continue

            # Fetch full game data via REST
            try:
                old_feed = self._feed
                start_tc = self._last_timecode
                end_tc = msg.time_stamp

                logger.debug(
                    "REST fetch triggered for game %s (events=%s)",
                    self._game_pk,
                    msg.game_events,
                )
                new_feed = await self._api.game(self._game_pk)

                # Optionally fetch diff
                diff = None
                if self._config.fetch_diff and start_tc and end_tc:
                    try:
                        diff_resp = await self._api.get(
                            "game_diff",
                            gamePk=str(self._game_pk),
                            startTimecode=start_tc,
                            endTimecode=end_tc,
                        )
                        if isinstance(diff_resp, LiveFeedResponse):
                            diff = diff_resp
                    except (MlbApiError, httpx.HTTPError) as exc:
                        logger.warning("game_diff fetch failed: %s", exc)

                # Detect events
                detected = _detect_events(
                    old_feed,
                    new_feed,
                    ws_message=msg,
                    start_timecode=start_tc,
                    end_timecode=end_tc,
                    diff=diff,
                )

                self._feed = new_feed
                self._last_timecode = end_tc

                for event in detected:
                    await self._dispatch(event)

                # Check for game end
                if self._is_game_over(new_feed):
                    if self._config.postgame_linger > 0:
                        try:
                            await asyncio.wait_for(
                                self._stop.wait(),
                                timeout=self._config.postgame_linger,
                            )
                        except asyncio.TimeoutError:
                            pass
                    return

            except (MlbApiError, httpx.HTTPError) as exc:
                logger.warning("REST fetch after WS notification failed: %s", exc)
                continue

    # -- Internal: REST polling fallback --

    async def _watch_rest(self) -> None:
        """Fallback watch loop using REST polling."""
        async for feed, timecode in _rest_poll(
            self._game_pk, self._api, self._config, self._stop, self._feed
        ):
            if self._stop.is_set():
                return

            old_feed = self._feed
            start_tc = self._last_timecode

            # Optionally fetch diff
            diff = None
            if self._config.fetch_diff and start_tc and timecode:
                try:
                    diff_resp = await self._api.get(
                        "game_diff",
                        gamePk=str(self._game_pk),
                        startTimecode=start_tc,
                        endTimecode=timecode,
                    )
                    if isinstance(diff_resp, LiveFeedResponse):
                        diff = diff_resp
                except (MlbApiError, httpx.HTTPError) as exc:
                    logger.warning("game_diff fetch failed: %s", exc)

            detected = _detect_events(
                old_feed,
                feed,
                start_timecode=start_tc,
                end_timecode=timecode,
                diff=diff,
            )

            self._feed = feed
            self._last_timecode = timecode

            for event in detected:
                await self._dispatch(event)

            if self._is_game_over(feed):
                if self._config.postgame_linger > 0:
                    try:
                        await asyncio.wait_for(
                            self._stop.wait(),
                            timeout=self._config.postgame_linger,
                        )
                    except asyncio.TimeoutError:
                        pass
                return

    # -- Internal: dispatch --

    async def _dispatch(self, event: GameEventData) -> None:
        """Dispatch an event to registered handlers and stream queues."""
        et = str(event.event_type)

        # Fire callbacks
        handlers = self._handlers.get(et, [])
        if handlers:
            logger.debug(
                "Dispatching %s to %d handler(s) for game %s",
                et,
                len(handlers),
                event.game_pk,
            )
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                logger.exception("Error in handler for %s", et)

        # Push to stream queues
        for filter_set, queue in self._queues:
            if filter_set is None or et in filter_set:
                await queue.put(event)

    # -- Internal: game over check --

    @staticmethod
    def _is_game_over(feed: LiveFeedResponse) -> bool:
        if feed.game_data and feed.game_data.status:
            state = feed.game_data.status.abstract_game_state
            return state == AbstractGameState.FINAL if state else False
        return False


# ---------------------------------------------------------------------------
# SyncLiveGameClient
# ---------------------------------------------------------------------------


class SyncLiveGameClient:
    """Synchronous live game client.

    Runs an :class:`LiveGameClient` in a background thread. Callbacks
    registered via :meth:`on` are plain (non-async) functions.

    Usage::

        with SyncLiveGameClient(game_pk=745563) as client:

            @client.on(GameEvent.PITCH)
            def on_pitch(event: GameEventData):
                print(f"Pitch: {event.play_event.details.description}")

            client.watch()
    """

    def __init__(
        self,
        game_pk: int,
        *,
        config: LiveGameConfig | None = None,
    ) -> None:
        self._game_pk = game_pk
        self._config = config or LiveGameConfig()
        self._sync_handlers: dict[str, list[SyncHandler]] = {}
        self._feed: LiveFeedResponse | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._async_client: LiveGameClient | None = None

    @property
    def feed(self) -> LiveFeedResponse | None:
        """The most recent :class:`LiveFeedResponse`, or ``None``."""
        return self._feed

    @property
    def game_pk(self) -> int:
        """The game primary key being watched."""
        return self._game_pk

    def on(
        self,
        event_type: GameEvent | str | Sequence[GameEvent | str],
        handler: SyncHandler | None = None,
    ) -> Callable[[SyncHandler], SyncHandler]:
        """Register a synchronous callback for one or more event types."""
        types = [event_type] if isinstance(event_type, str) else list(event_type)

        def _register(fn: SyncHandler) -> SyncHandler:
            for t in types:
                self._sync_handlers.setdefault(str(t), []).append(fn)
            return fn

        if handler is not None:
            _register(handler)
            return _register
        return _register

    def watch(self) -> None:
        """Watch the game until it ends or :meth:`stop` is called.

        Blocks the calling thread.
        """
        self._loop = asyncio.new_event_loop()
        try:
            self._loop.run_until_complete(self._run())
        finally:
            self._loop.close()
            self._loop = None

    def stop(self) -> None:
        """Signal the watch loop to stop. Thread-safe."""
        if self._async_client and self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._async_client._stop.set)

    def close(self) -> None:
        """Stop watching and release resources."""
        self.stop()

    def __enter__(self) -> SyncLiveGameClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    async def _run(self) -> None:
        """Internal async entry point run in the event loop."""
        async with LiveGameClient(self._game_pk, config=self._config) as client:
            self._async_client = client

            # Wrap sync handlers as async and register them
            for event_type, handlers in self._sync_handlers.items():
                for sync_fn in handlers:

                    async def _wrapper(
                        event: GameEventData,
                        _fn: SyncHandler = sync_fn,
                    ) -> None:
                        _fn(event)
                        # Update feed reference
                        if event.feed:
                            self._feed = event.feed

                    client.on(event_type, handler=_wrapper)

            # Also track feed updates for all events
            async def _track_feed(event: GameEventData) -> None:
                if event.feed:
                    self._feed = event.feed

            client.on(GameEvent.UPDATE, handler=_track_feed)

            await client.watch()
