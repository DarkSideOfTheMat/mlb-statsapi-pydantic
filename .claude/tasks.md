# mlb-statsapi-pydantic — Implementation Tasks

> Pydantic v2 typed client for the MLB Stats API.
> Reference: [toddrob99/MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI)
> Approach: TDD — write tests first, then implement until green.

---

## Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| `extra="allow"` on all models | Yes | MLB API adds fields without notice; strict breaks clients |
| `alias_generator=to_camel` | Yes | Auto snake_case ↔ camelCase without per-field aliases |
| httpx (not requests) | Yes | Native async support, modern API |
| `src/` layout | Yes | Packaging best practice, avoids import shadowing |
| Tiered endpoint coverage | Yes | Ship Tier 1 fast, expand incrementally |
| `IdNameLink.name` optional | Yes | Some API refs omit `name` (e.g. `springVenue`) |

## Package Structure

```
src/mlb_statsapi/
├── __init__.py              # Public re-exports
├── exceptions.py            # MlbApiError, MlbValidationError
├── client/
│   ├── __init__.py
│   ├── _base.py             # Shared: URL building, param validation, response parsing
│   ├── sync_client.py       # MlbClient (httpx sync)
│   └── async_client.py      # AsyncMlbClient (httpx async)
├── endpoints/
│   ├── __init__.py
│   └── registry.py          # EndpointDef dataclass + 60+ endpoint definitions
└── models/
    ├── __init__.py           # Re-exports
    ├── _base.py              # MlbBaseModel, BaseResponse, IdNameLink, CodeDescription
    ├── enums.py              # GameType, GameState, HandCode, PositionType, etc.
    ├── sports.py             # Sport, SportsResponse
    ├── divisions.py          # Division, DivisionsResponse
    ├── leagues.py            # League, LeaguesResponse
    ├── venues.py             # Venue, VenuesResponse
    ├── seasons.py            # Season, SeasonsResponse
    ├── teams.py              # Team, TeamsResponse, TeamRecord, Roster
    ├── people.py             # Person, PeopleResponse, PrimaryPosition
    ├── schedule.py           # ScheduleResponse, ScheduleDate, ScheduleGame, GameStatus
    ├── standings.py          # StandingsResponse, StandingsRecord, TeamStanding
    ├── game.py               # BoxscoreResponse, LinescoreResponse, LiveFeedResponse
    ├── stats.py              # StatGroup, StatSplit, LeaderCategory, StatsResponse
    ├── transactions.py
    ├── draft.py
    ├── awards.py
    ├── attendance.py
    ├── jobs.py
    └── meta.py
```

---

## Tasks

### Task 1: Project Setup & TDD Foundation
**Status:** not started
**Goal:** Repo, tooling, deps, directory skeleton, and first test suite so every future task starts with red tests.

**Steps:**
1. `git init`, create GitHub repo via `gh repo create`
2. Create `pyproject.toml` — hatchling build system
   - deps: `pydantic>=2.0`, `httpx>=0.25`
   - dev deps: `pytest`, `pytest-asyncio`, `respx`, `ruff`, `mypy`
   - `requires-python = ">=3.10"`
3. `.gitignore` (Python template), `LICENSE` (MIT)
4. Create full directory skeleton (all `__init__.py` files, empty modules)
5. Create Python venv, install deps in editable mode (`pip install -e ".[dev]"`)
6. Write `src/mlb_statsapi/exceptions.py` — `MlbApiError`, `MlbValidationError`
7. Write initial test stubs in `tests/`:
   - `conftest.py` with fixture loading helper
   - `tests/fixtures/` — fetch & save JSON from live API: sports, teams (sportId=1), schedule, people/660271, standings
   - `tests/test_models/test_base.py` — tests for `MlbBaseModel`, `BaseResponse`, `IdNameLink`, `CodeDescription`
   - `tests/test_models/test_enums.py` — tests for all enum types
8. Run `pytest` — confirm tests exist and fail (red)
9. Initial commit + push

**Verification:** `pytest` runs, discovers tests, all fail (no implementations yet). `ruff check` clean. Venv works.

---

### Task 2: Base Models & Enums
**Status:** not started
**Depends on:** Task 1
**Goal:** Implement foundation models until Task 1 tests go green.

**Files to create:**
- `src/mlb_statsapi/models/_base.py`
  - `MlbBaseModel(BaseModel)` — `ConfigDict(populate_by_name=True, extra="allow", alias_generator=to_camel)`
  - `BaseResponse(MlbBaseModel)` — `copyright: str`
  - `IdNameLink(MlbBaseModel)` — `id: int, name: str | None = None, link: str`
  - `CodeDescription(MlbBaseModel)` — `code: str, description: str`
- `src/mlb_statsapi/models/enums.py`
  - `GameType`, `AbstractGameState`, `HandCode`, `PositionType` as `StrEnum`
- `src/mlb_statsapi/models/__init__.py` — re-exports

**Verification:** `pytest tests/test_models/test_base.py tests/test_models/test_enums.py` all green.

---

### Task 3: Simple Domain Models (sports, divisions, leagues, venues, seasons)
**Status:** completed
**Depends on:** Task 2
**Goal:** TDD the simplest response models — flat arrays with minimal nesting.

**For each module:** write tests first using saved JSON fixtures, then implement.
- `sports.py` — `Sport`, `SportsResponse`
- `divisions.py` — `Division`, `DivisionsResponse`
- `leagues.py` — `League`, `LeaguesResponse`
- `venues.py` — `Venue`, `VenuesResponse`
- `seasons.py` — `Season`, `SeasonsResponse`

**Verification:** `pytest tests/test_models/` all green. Models validate against real API fixtures.

---

### Task 4: Teams & People Models
**Status:** completed
**Depends on:** Task 2
**Goal:** TDD the team and player models with nested references.

- `teams.py` — `Team`, `TeamsResponse`, `TeamRecord`, `Roster`, `RosterEntry`
  - Nested: `IdNameLink` for venue, league, division, spring_league
- `people.py` — `Person`, `PeopleResponse`, `PrimaryPosition`, `BatPitchSide`
  - Nested: `CodeDescription` for bat_side, pitch_hand
  - Date fields as `datetime.date`

**Verification:** `pytest tests/test_models/test_teams.py tests/test_models/test_people.py` green.

---

### Task 5: Schedule & Standings Models
**Status:** completed
**Depends on:** Task 2
**Goal:** TDD the most complex response hierarchies.

- `schedule.py` — `ScheduleResponse`, `ScheduleDate`, `ScheduleGame`, `GameStatus`, `ScheduleTeam`
  - Hierarchy: dates → games → teams.{away,home}
  - Multiple status representations (abstract, coded, detailed)
- `standings.py` — `StandingsResponse`, `StandingsRecord`, `TeamStanding`, `Streak`
  - Division-grouped team records

**Verification:** `pytest tests/test_models/test_schedule.py tests/test_models/test_standings.py` green.

---

### Task 6: Game Models (Boxscore, Linescore, Live Feed)
**Status:** completed
**Depends on:** Task 4 (reuses Team/Person models)
**Goal:** TDD the deepest, most complex models.

- `game.py` — `BoxscoreResponse`, `LinescoreResponse`, `LiveFeedResponse`
  - Boxscore: `teams.{away,home}` with batting/pitching/fielding stats, players dict keyed by `"ID{playerId}"`
  - Linescore: innings array with home/away runs/hits/errors
  - LiveFeed: `game_data`, `live_data.plays`, `live_data.linescore`, `live_data.boxscore`
- `stats.py` — `StatGroup`, `StatSplit`, `LeaderCategory`, `StatsResponse`

**Verification:** `pytest tests/test_models/test_game.py tests/test_models/test_stats.py` green.

---

### Task 7: Endpoint Registry
**Status:** not started
**Depends on:** Tasks 2–6
**Goal:** Define all 60+ MLB API endpoints in a typed registry.

- `endpoints/registry.py`
  - `EndpointDef` frozen dataclass: `url_template`, `path_params`, `query_params`, `required_params`, `default_version`, `response_model`
  - Registry `dict[str, EndpointDef]` covering all endpoints
  - Tier 1 (~15): full model — schedule, teams, people, standings, game, boxscore, linescore, stats_leaders, roster, seasons, sports
  - Tier 2 (~15): model, no convenience method — divisions, leagues, venues, transactions, draft, awards
  - Tier 3 (~30): `BaseResponse` — remaining endpoints accessible via `client.get()`
- Tests: endpoint URL construction, required param validation

**Verification:** `pytest tests/test_client/test_endpoint_registry.py` green.

---

### Task 8: Client Implementation (Sync + Async)
**Status:** not started
**Depends on:** Task 7
**Goal:** Build the httpx-based client with typed convenience methods.

- `client/_base.py` — `_ClientMixin`
  - `_build_request(endpoint, **params) -> (url, query_params)`
  - `_parse_response(endpoint, data) -> BaseResponse`
  - Required param validation
- `client/sync_client.py` — `MlbClient`
  - Convenience methods: `schedule()`, `teams()`, `person()`, `standings()`, `boxscore()`, `linescore()`, `roster()`, `player_stats()`, `league_leaders()`, `get()`
- `client/async_client.py` — `AsyncMlbClient` (same interface, `async def`)
- Tests: mock httpx with `respx`, test URL building, param validation, error handling

**Verification:** `pytest tests/test_client/` all green.

---

### Task 9: Remaining Models & Public API Polish
**Status:** not started
**Depends on:** Task 8
**Goal:** Fill in Tier 2 models and finalize the package surface.

- Implement remaining model files: `transactions.py`, `draft.py`, `awards.py`, `attendance.py`, `jobs.py`, `meta.py`
- `src/mlb_statsapi/__init__.py` — export `MlbClient`, `AsyncMlbClient`, all response models
- `src/mlb_statsapi/py.typed` — PEP 561 marker
- `models/__init__.py` — complete re-exports

**Verification:** `mypy src/mlb_statsapi/` passes. `ruff check src/` clean.

---

### Task 10: Integration Tests & Smoke Test
**Status:** not started
**Depends on:** Task 9
**Goal:** Validate against the live MLB API.

- `tests/test_integration/test_live_api.py` — marked `@pytest.mark.integration`
  - Hit live API for key endpoints, validate parsing
  - Sports, teams, schedule, person, standings, boxscore
- Manual smoke test:
  ```python
  from mlb_statsapi import MlbClient
  client = MlbClient()
  schedule = client.schedule(date="03/27/2026")
  print(schedule.dates[0].games[0].teams.home.team.name)
  ```
- `pyproject.toml` — add `[tool.pytest.ini_options]` markers config

**Verification:** `pytest tests/ -m "not integration"` all green. `pytest tests/ -m integration` passes against live API.
