# Live Game Client

Watch MLB games in real time using WebSocket push notifications with optional REST enrichment.

The live game client connects to MLB's gameday WebSocket at
`wss://ws.statsapi.mlb.com/api/v1/game/push/subscribe/gameday/<gamePk>`
to receive lightweight notifications, then fetches full game data via REST
based on your configured granularity.

## Installation

The live client requires the `httpx-ws` package, which is included as a dependency:

```bash
pip install mlb-statsapi-pydantic
```

## Quick Start

```python
import asyncio
from mlb_statsapi import LiveGameClient, GameEvent, GameEventData

async def main():
    client = LiveGameClient(game_pk=824782)

    @client.on(GameEvent.PITCH)
    async def on_pitch(event: GameEventData):
        pe = event.play_event
        if pe and pe.details:
            print(f"Pitch: {pe.details.description}")

    @client.on(GameEvent.RUN)
    async def on_run(event: GameEventData):
        ls = event.feed.live_data.linescore
        print(f"Score: {ls.teams.away.runs}-{ls.teams.home.runs}")

    await client.watch()

asyncio.run(main())
```

## Architecture

```
WebSocket ──push──> WsMessage ──filter──> REST fetch ──> Event detection ──> Callbacks
                                  |                       (LiveFeedResponse)
                                  no
                                  |
                                  v
                             Skip update
```

1. **WebSocket** receives `WsMessage` notifications (~every 10-30s during play)
2. **Granularity filter** checks if `gameEvents`/`logicalEvents` match your configured triggers
3. **REST enrichment** fetches the full `LiveFeedResponse` (or `game_diff`)
4. **Event detection** compares old vs new feed state to classify what happened
5. **Dispatch** fires registered callbacks and pushes to stream queues

## Clients

### AsyncMlbClient (Async)

```python
from mlb_statsapi import LiveGameClient, LiveGameConfig

async with LiveGameClient(game_pk=824782) as client:
    @client.on(GameEvent.PITCH)
    async def on_pitch(event: GameEventData):
        ...

    await client.watch()
```

### SyncLiveGameClient (Sync)

Runs the async client in a background thread. Callbacks are plain functions:

```python
from mlb_statsapi import SyncLiveGameClient, GameEvent, GameEventData

with SyncLiveGameClient(game_pk=824782) as client:
    @client.on(GameEvent.PITCH)
    def on_pitch(event: GameEventData):
        print(f"Pitch: {event.play_event.details.description}")

    client.watch()  # blocks until game ends
```

## Event Types

Events are detected by comparing consecutive `LiveFeedResponse` states after REST enrichment:

| Event | Trigger |
|---|---|
| `WS_MESSAGE` | Every raw WebSocket notification (no REST fetch needed) |
| `UPDATE` | Any change to the live feed |
| `GAME_START` | `AbstractGameState` transitions to `Live` |
| `GAME_END` | `AbstractGameState` transitions to `Final` |
| `GAME_STATE_CHANGE` | Any `AbstractGameState` transition |
| `PITCH` | New pitch event in current play's `play_events` |
| `HIT` | Pitch with `details.is_in_play == True` |
| `PLAY_COMPLETE` | New completed play in `all_plays` |
| `STRIKEOUT` | Completed play with strikeout event type |
| `WALK` | Completed play with walk/intentional walk |
| `HOME_RUN` | Completed play with home run event type |
| `RUN` | Score change detected in linescore |
| `INNING_CHANGE` | `current_inning` or `inning_half` changes |
| `SUBSTITUTION` | Play event with `is_substitution == True` |

## Registering Callbacks

### Decorator

```python
@client.on(GameEvent.PITCH)
async def on_pitch(event: GameEventData):
    ...
```

### Direct registration

```python
async def my_handler(event: GameEventData):
    ...

client.on(GameEvent.PITCH, handler=my_handler)
```

### Multiple events

```python
@client.on([GameEvent.STRIKEOUT, GameEvent.WALK, GameEvent.HOME_RUN])
async def on_at_bat_result(event: GameEventData):
    print(f"{event.event_type}: {event.play.result.description}")
```

## Async Iterator (Stream)

Use `stream()` as an alternative to callbacks:

```python
async with LiveGameClient(game_pk=824782) as client:
    # Start watch in the background
    watch_task = asyncio.create_task(client.watch())

    async for event in client.stream(GameEvent.PITCH, GameEvent.RUN):
        print(event.event_type)

    await watch_task
```

Pass no arguments to receive all events:

```python
async for event in client.stream():
    ...
```

## Granularity

Controls which WebSocket notifications trigger a REST fetch. Lower granularity = fewer REST calls = less bandwidth.

| Preset | Triggers on |
|---|---|
| `EVERY_UPDATE` | Every WebSocket message |
| `EVERY_PITCH` | Pitch results, play outcomes (default) |
| `EVERY_PLAY` | Play completions, substitutions |
| `SCORING_ONLY` | `hit_into_play_score` events |
| `CUSTOM` | User-provided list of trigger values |

```python
from mlb_statsapi import LiveGameConfig, FetchGranularity

# Only fetch on scoring plays
config = LiveGameConfig(granularity=FetchGranularity.SCORING_ONLY)
client = LiveGameClient(game_pk=824782, config=config)
```

### Custom triggers

```python
config = LiveGameConfig(
    granularity=FetchGranularity.CUSTOM,
    custom_triggers=["caught_stealing_2b", "runnersInScoringPosition"],
)
```

Custom triggers match against both `gameEvents` and `logicalEvents` from the WebSocket message.

## Configuration

`LiveGameConfig` controls all client behavior:

```python
config = LiveGameConfig(
    # Granularity
    granularity=FetchGranularity.EVERY_PITCH,
    custom_triggers=[],           # for CUSTOM granularity

    # Enrichment
    fetch_diff=False,             # also fetch game_diff between timecodes

    # REST fallback (when WebSocket unavailable)
    poll_interval=10.0,           # seconds between REST polls
    pregame_poll_interval=60.0,   # seconds between polls in Preview state
    use_rest_fallback=True,       # fall back to REST if WS fails

    # WebSocket
    ws_reconnect_delay=2.0,       # initial reconnect delay (seconds)
    ws_max_reconnect_delay=60.0,  # max reconnect delay after backoff

    # Lifecycle
    postgame_linger=0.0,          # seconds to stay connected after game ends
    max_retries=5,                # max retries for initial REST fetch
    retry_delay=5.0,              # seconds between retries
)
```

## GameEventData

Every callback receives a `GameEventData` object:

| Field | Type | Description |
|---|---|---|
| `event_type` | `GameEvent` | Which event triggered this callback |
| `game_pk` | `int` | Game primary key |
| `feed` | `LiveFeedResponse` | Current full game state |
| `previous_feed` | `LiveFeedResponse` | Previous game state |
| `ws_message` | `WsMessage` | Raw WebSocket notification that triggered the fetch |
| `play` | `Play` | The relevant play (for play-related events) |
| `play_event` | `PlayEvent` | The relevant pitch/action (for pitch-related events) |
| `start_timecode` | `str` | Timecode of previous update |
| `end_timecode` | `str` | Timecode of current update |
| `diff` | `LiveFeedResponse` | Diff feed (when `fetch_diff=True`) |

## REST API Access

The underlying REST client is available for ad-hoc queries:

```python
async with LiveGameClient(game_pk=824782) as client:
    # Use client.api for any REST call
    boxscore = await client.api.game_boxscore(824782)

    @client.on(GameEvent.HOME_RUN)
    async def on_hr(event: GameEventData):
        # Fetch additional data on demand
        batter_id = event.play.matchup.batter.id
        person = await client.api.person(batter_id)
        print(f"Home run by {person.people[0].full_name}!")

    await client.watch()
```

## WebSocket Message Model

The raw WebSocket notifications are parsed into `WsMessage`:

```python
from mlb_statsapi.models import WsMessage

# Fields available on every WS notification:
msg.time_stamp       # "20260404_201235"
msg.game_pk          # "824782"
msg.update_id        # UUID string
msg.wait             # server-suggested poll interval (seconds)
msg.game_events      # ["called_strike"]
msg.logical_events   # ["countChange", "count01", "basesEmpty"]
msg.change_event     # ChangeEvent(type="new_entry")
msg.is_delay         # True/False/None
```

### Known gameEvents values

Pitch results: `ball`, `called_strike`, `swinging_strike`, `foul`, `foul_tip`, `foul_bunt`, `blocked_ball`, `hit_into_play`, `hit_into_play_no_out`, `hit_into_play_score`

Play outcomes: `single`, `double`, `triple`, `field_out`, `strikeout`, `walk`, `force_out`, `sac_fly`, `grounded_into_double_play`, `caught_stealing_2b`

Other: `at_bat_start`, `pitching_substitution`, `offensive_substitution`, `defensive_switch`, `batter_timeout`, `mound_visit`, `game_advisory`

### Known logicalEvents values

Count: `countChange`, `count00` through `count42`

Batter: `newBatter`, `newRightHandedHit`, `newLeftHandedHit`, `batterSwitchedToLeftHanded`, `batterSwitchedToRightHanded`

Baserunners: `basesEmpty`, `runnerOnFirst`, `runnerOnSecond`, `runnerOnThird`, `runnersOnFirstAndSecond`, `runnersOnFirstAndThird`, `runnersOnSecondAndThird`, `runnersInScoringPosition`, `basesLoaded`

Inning: `newHalfInning`, `midInning`

Pitcher: `pitcherChange`, `pitcherChangeComplete`

Defense: `defensiveSubstitution`

### changeEvent types

- `new_entry` -- new play event added
- `full_refresh` -- full game state refresh
- `correction` -- correction to previous data (may include `changed_at_bat_indexes`)

## Error Handling

- **WebSocket disconnect**: Auto-reconnects with exponential backoff (2s to 60s)
- **WebSocket unavailable**: Falls back to REST polling when `use_rest_fallback=True`
- **REST errors**: Retries with backoff up to `max_retries`
- **Callback errors**: Logged but do not crash the client
- **Unknown WS message format**: Logged and skipped
