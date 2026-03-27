# MLB Stats API — Research Reference

## API Overview

- **Base URL:** `https://statsapi.mlb.com/api/`
- **Versions:** Most endpoints use `v1`; live game feed uses `v1.1`
- **Auth:** None required for public data (some analytics/statcast endpoints need auth)
- **Response format:** JSON; all responses include a `copyright` field

---

## Response Patterns

### Common Root Structure
Every response wraps data in a named array: `{"copyright": "...", "teams": [...]}`, `{"people": [...]}`, `{"dates": [...]}`, etc.

### Reference Object Pattern — `{id, name, link}`
Used everywhere for cross-references (teams, venues, leagues, divisions, people). Variations:
- Minimal: `{id, link}` (e.g. `springVenue`)
- Standard: `{id, name, link}`
- Extended: `{id, name, link, abbreviation, ...}` (e.g. `springLeague`)

### Code/Description Pattern — `{code, description}`
Used for: `batSide`, `pitchHand`, `gameType`, position types.

### Enum-like Fields
| Field | Values |
|-------|--------|
| `abstractGameState` | Preview, Live, Final |
| `codedGameState` | P, S, I, F, and others |
| `gameType` | R (regular), S (spring), F (wild card), D (division), L (league), W (world series), C, P, A, E, I |
| `batSide/pitchHand code` | L, R, S (switch) |
| `dayNight` | day, night |
| `positionType` | Pitcher, Catcher, Infielder, Outfielder, Hitter, Runner, etc. |

---

## Key Endpoint Response Structures

### Sports (`/api/v1/sports`)
Flat array. Fields: `id`, `code`, `link`, `name`, `abbreviation`, `sortOrder`, `activeStatus` (boolean).

### Teams (`/api/v1/teams?sportId=1`)
Rich objects. Notable fields:
- Multiple name variants: `name`, `teamName`, `shortName`, `franchiseName`, `clubName`
- Nested refs: `venue`, `springVenue`, `league`, `division`, `springLeague`, `sport`
- `season` (int), `firstYearOfPlay` (string), `active` (boolean), `allStarStatus` (string)

### Schedule (`/api/v1/schedule?sportId=1&date=MM/DD/YYYY`)
Nested hierarchy: root → `dates[]` → `games[]` → `teams.{away,home}`
- Root-level aggregates: `totalItems`, `totalEvents`, `totalGames`, `totalGamesInProgress`
- Same aggregates repeated per date
- Game fields: `gamePk`, `gameGuid`, `link`, `gameType`, `season`, `gameDate` (ISO 8601), `officialDate` (YYYY-MM-DD)
- `status` object: `abstractGameState`, `codedGameState`, `detailedState`, `statusCode`, `startTimeTBD`
- `venue` ref, `dayNight` field

### People (`/api/v1/people/{id}`)
Single person wrapped in `people[]` array. Notable fields:
- `id`, `fullName`, `firstName`, `lastName`, `primaryNumber`
- `birthDate` (YYYY-MM-DD), `currentAge`, `birthCity`, `birthCountry`
- `height` (string, e.g. `6' 2"`), `weight` (int)
- `primaryPosition` — has `code`, `name`, `type`, `abbreviation`
- `batSide`, `pitchHand` — `{code, description}`
- `strikeZoneTop`, `strikeZoneBottom` (floats)
- `mlbDebutDate` (optional), `nickName` (optional)
- Name variants: `useName`, `boxscoreName`, `nickName`

### Standings
Division-grouped. Structure: `records[]` → `teamRecords[]`
- Team record fields: `wins`, `losses`, `winningPercentage`, `gamesBack`, `wildCardGamesBack`, `divisionRank`, `wildCardRank`, `eliminationNumber`
- `streak` object, `leagueRecord`, `records` (splits)

### Boxscore
`teams.{away,home}` each with:
- `teamStats.{batting,pitching,fielding}` — aggregate stats
- `players` dict keyed by `"ID{playerId}"` — individual player stats
- `battingOrder` array, `info` array, `note` strings

### Linescore
`innings[]` array with `home`/`away` each having `runs`, `hits`, `errors` per inning.
Top-level `teams.{home,away}` with game totals.

### Live Feed (`/api/v1.1/game/{gamePk}/feed/live`)
Largest response. Top-level: `gameData`, `liveData`
- `gameData`: datetime, status, teams, players, venue, weather, probablePitchers
- `liveData.plays`: allPlays, currentPlay, scoringPlays
- `liveData.linescore`: same as linescore endpoint
- `liveData.boxscore`: same as boxscore endpoint

---

## Reference Library (toddrob99/MLB-StatsAPI)

### 27 Public Functions
**Schedule/Game:** `schedule`, `boxscore`, `boxscore_data`, `linescore`, `last_game`, `next_game`, `game_scoring_plays`, `game_scoring_play_data`, `game_highlights`, `game_highlight_data`, `game_pace`, `game_pace_data`

**Player:** `player_stats`, `player_stat_data`, `lookup_player`, `latest_season`

**Team:** `lookup_team`, `roster`, `team_leaders`, `team_leader_data`

**League:** `league_leaders`, `league_leader_data`, `standings`, `standings_data`

**Utility:** `meta`, `notes`, `get`

### Endpoint System
60+ endpoints defined in `endpoints.py` as a dict. Each has:
- `url` — template with `{ver}` and `{param}` placeholders
- `path_params` — dict with type, default, required, leading/trailing slash
- `query_params` — list of allowed query param names
- `required_params` — list of lists (OR combinations)
- `note` — developer guidance (optional)

### Key Details
- Only dependency: `requests`
- No type hints or Pydantic models
- Returns formatted strings (display) or raw dicts (data variants)
- Core `get()` function handles all HTTP, param validation, URL construction
- Uses `datetime.now().year` as default season
- Logger name: `"statsapi"`

---

## Meta Endpoint Types
Valid types for `/api/v1/meta?type=X`:
awards, baseballStats, eventTypes, freeGameTypes, gameStatus, gameTypes, hitTrajectories, jobTypes, languages, leagueLeaderTypes, logicalEvents, metrics, pitchCodes, pitchTypes, platforms, positions, reviewReasons, rosterTypes, runnerDetailTypes, scheduleTypes, scheduleEventTypes, situationCodes, sky, standingsTypes, statGroups, statTypes, violationTypes, windDirection

---

## Known Quirks
- Some fields appear/disappear depending on game state or context
- `springVenue` has only `{id, link}` — no `name`
- Boxscore `players` dict uses string keys like `"ID660271"` instead of integer keys
- Date formats vary: `gameDate` is ISO 8601, `officialDate` is YYYY-MM-DD, schedule query uses MM/DD/YYYY
- `height` is a display string (`6' 2"`) not a numeric value
- `firstYearOfPlay` on teams is a string, not int
