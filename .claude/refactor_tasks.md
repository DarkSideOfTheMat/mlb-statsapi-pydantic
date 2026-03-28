# Model Refactoring Tasks

> Branch: `refactor-models`
> Based on comprehensive code review of all 20 model files.

---

## Task 1: Consolidate shared models into `_base.py`
**Status:** completed
**Blocked by:** —

Deduplicate models repeated across files:

- **PersonRef** (6 duplicates): `PersonRef` (livefeed), `BoxscorePersonRef` (game), `TransactionPerson` (transactions), `JobPerson` (jobs), `LeaderPersonRef` (stats), `DraftPerson` (draft). Create single `PersonRef` in `_base.py` with `id: PersonId`, `full_name: str | None`, `link: str | None`.
- **PositionRef** (3 duplicates): `PrimaryPosition` (people), `PositionRef` (livefeed), `BoxscorePosition` (game). Create single `PositionRef` in `_base.py` with `code: str`, `name: str | None`, `type: str | None`, `abbreviation: str | None`.
- **WinLossRecord** (4 duplicates): `LeagueRecord` (schedule), `StandingsLeagueRecord` (standings), `GameDataTeamRecord` (livefeed), plus `SplitRecord` variant. Create single `WinLossRecord` in `_base.py`.
- **GameStatus** (2 duplicates): `schedule.GameStatus`, `livefeed.GameDataStatus`. Consolidate into one in `_base.py` or `schedule.py`.

Update all imports across models and tests.

---

## Task 2: Define custom ID types (NewType) for entity IDs
**Status:** not started
**Blocked by:** —

Create `NewType` definitions in `_base.py` instead of bare `int`:

- `PersonId = NewType("PersonId", int)` — `PersonRef.id`, `Person.id`, `BoxscoreTeam.batters/pitchers/bench/bullpen/batting_order` items
- `TeamId = NewType("TeamId", int)` — `Team.id`, `GameDataTeam.id`, `BoxscorePlayer.parent_team_id`
- `GamePk = NewType("GamePk", int)` — `LiveFeedResponse.game_pk`, `ScheduleGame.game_pk`, `AttendanceGame.game_pk`

Keep `IdNameLink.id` as plain `int` since it's used generically across entity types.

**Verified data patterns:**
- `BoxscoreTeam.batters/pitchers/bench/bullpen/batting_order` contain **player IDs** (e.g., `608324`) that map to `players["ID608324"]`, NOT array indices.
- `Plays.scoring_plays`, `Play.pitch_index/action_index/runner_index`, `InningPlays.top/bottom` are **array indices** into sibling lists.

---

## Task 3: Wire up enums to model fields
**Status:** not started
**Blocked by:** Task 1

All four enums in `enums.py` are defined but never referenced by any model field:

- `GameType` → `ScheduleGame.game_type`, attendance `game_type.id`
- `AbstractGameState` → `GameStatus.abstract_game_state`
- `HandCode` → bat_side/pitch_hand `code` fields
- `PositionType` → `PositionRef.type`

Since the API may return unexpected values, consider using the enum but keeping `extra="allow"` or using a validator that falls back to `str`.

---

## Task 4: Add index-to-object helper properties
**Status:** not started
**Blocked by:** Task 1, Task 2

**Array index helpers** (indices into sibling arrays on the same object):
- `Plays.scoring_plays: list[int]` → `@property scoring_play_objects -> list[Play]` (indices into `all_plays`)
- `Play.pitch_index: list[int]` → `@property pitches -> list[PlayEvent]` (indices into `play_events`)
- `Play.action_index: list[int]` → `@property actions -> list[PlayEvent]` (indices into `play_events`)
- `Play.runner_index: list[int]` → `@property indexed_runners -> list[Runner]` (indices into `runners`)
- `InningPlays.top/bottom: list[int]` — indices into parent `Plays.all_plays`; document clearly, consider if helper is feasible

**Player ID lookup helpers** (PersonId → player object via `players` dict):
- `BoxscoreTeam.batters/pitchers/bench/bullpen/batting_order: list[PersonId]` → `@property batter_players`, `pitcher_players`, `bench_players`, `bullpen_players`, `batting_order_players` that resolve against `players[f"ID{pid}"]`

---

## Task 5: Fix stringly-typed date/datetime fields
**Status:** not started
**Blocked by:** —

Convert `str` date fields to proper types (following `seasons.py` and `people.py` pattern):

**→ `datetime.date`:**
- `ScheduleDate.date` (`"2024-07-01"`)
- `Transaction.date`, `effective_date`, `resolution_date` (`"2024-03-01"`)
- `DraftPerson.birth_date`

**→ `datetime.datetime`:**
- `ScheduleGame.game_date` (`"2024-07-01T19:07:00Z"`)
- `TeamStanding.last_updated`, `StandingsRecord.last_updated` (`"2025-12-27T17:29:50Z"`)
- `PlayEvent.start_time`, `end_time`
- `PlayAbout.start_time`, `end_time`
- `Play.play_end_time`
- `AttendanceRecord.attendance_high_date`, `attendance_low_date`

---

## Task 6: Standardize season field type across models
**Status:** not started
**Blocked by:** —

Inconsistent `season` typing across models:
- `int | None` in `Team`
- `str` in `Division`, `TeamStanding`, `LeaderEntry`, `Season.season_id`
- `str | None` in `Venue`, `ScheduleGame`

Standardize on `int` (more useful for comparisons). Add Pydantic validators to coerce `str → int` where the API returns strings.

---

## Task 7: Replace weak `MlbBaseModel`/`dict` catch-all types with proper models
**Status:** not started
**Blocked by:** Task 1

17 fields use `MlbBaseModel` or `dict` as catch-alls. Replace with typed models:

**game.py:**
- `BoxscorePlayer.stats/season_stats` → `PlayerStats` model with batting/pitching/fielding
- `BoxscoreTeamStats.batting/pitching/fielding` → typed stat models (`BattingStats`, `PitchingStats`, `FieldingStats`)
- `BoxscoreTeam.info/note` → `BoxscoreInfo` model with `title` + `field_list: list[BoxscoreInfoField]`
- `BoxscorePlayer.game_status/status` → typed models

**livefeed.py:**
- `GameData.game` → `GameInfo` model
- `GameData.datetime` → `GameDateTime` model
- `GameData.game_info` → `GameInfoDetails` model (attendance, firstPitch, gameDurationMinutes)
- `GameData.review` → `ReviewInfo` model
- `GameData.flags` → `GameFlags` model (noHitter, perfectGame)
- `LiveData.linescore` → reuse `LinescoreResponse` (minus copyright) or create `Linescore` base
- `LiveData.boxscore` → reuse `BoxscoreResponse` (minus copyright) or create `Boxscore` base
- `Matchup.batter_hot_cold_zones/pitcher_hot_cold_zones` → `HotColdZone` model

**draft.py:**
- `DraftPick.draft_type` → `CodeDescription` from `_base.py`
- `DraftPerson.primary_position` → shared `PositionRef`

**attendance.py:**
- `AttendanceRecord.game_type` → `GameTypeRef` from stats.py or shared model

**stats.py:**
- `StatSplit.stat` → typed stat dicts or keep `dict` with better type annotation

---

## Task 8: Add computed properties for derived data
**Status:** not started
**Blocked by:** Task 1, Task 5

- `Person.height_inches -> int | None` — parse `"6' 2\""` → `74`
- `WinLossRecord.win_pct -> float | None` — parse `".512"` → `0.512`
- `TeamStanding.games_back_float -> float | None` — parse `"-"` → `0.0`, `"5.0"` → `5.0`
- `DraftPick.pick_value_amount -> float | None` — parse `"9200000.00"` → `9200000.0`
- `DraftPick.signing_bonus_amount -> float | None` — same pattern

---

## Task 9: Add commonly-accessed missing fields
**Status:** not started
**Blocked by:** Task 1, Task 2

Fields currently hidden in `extra` that users would commonly access:

**standings.py `TeamStanding`:**
- `wins: int`, `losses: int`, `winning_percentage: str`
- `runs_scored: int`, `runs_allowed: int`, `run_differential: int`
- `division_champ: bool`, `division_leader: bool`, `clinched: bool`
- `elimination_number: str | None`, `magic_number: str | None`
- `wild_card_elimination_number: str | None`

**livefeed.py `GameData`:**
- `players: dict[str, PersonRef] | None` — full player dict keyed by `"ID{playerId}"`

**schedule.py `ScheduleGame`:**
- `series_description: str | None`, `games_in_series: int | None`, `series_game_number: int | None`

**stats.py `LeaderEntry`:**
- `num_teams: int | None`

Update tests to cover new fields where fixture data exists.

---

## Task 10: Update all tests and verify everything passes
**Status:** not started
**Blocked by:** Tasks 1–9

- Update all test imports to use consolidated models
- Add tests for new helper properties (index-to-object, computed properties)
- Add tests for new ID types
- Run full test suite: `pytest tests/test_models/ tests/test_client/`
- Run integration tests: `pytest tests/test_integration/ -m integration`
- Run `mypy src/mlb_statsapi` — strict, 0 errors
- Run `ruff check src/` — clean
