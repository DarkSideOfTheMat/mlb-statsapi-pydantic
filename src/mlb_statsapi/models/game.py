"""Game models — boxscore and linescore.

Endpoints:
- ``/api/v1/game/{gamePk}/boxscore``
- ``/api/v1/game/{gamePk}/linescore``

The boxscore provides aggregate and per-player statistics for a completed
or in-progress game. The linescore provides the inning-by-inning scoring
breakdown.
"""

from __future__ import annotations

from mlb_statsapi.models._base import (
    BaseResponse,
    CodeDescription,
    MlbBaseModel,
    PersonId,
    PersonRef,
    PositionRef,
    TeamId,
)
from mlb_statsapi.models.enums import HalfInning
from mlb_statsapi.models.teams import Team

StatValue = int | float | str | None
"""Type for individual stat values returned by the API."""

# ---------------------------------------------------------------------------
# Linescore
# ---------------------------------------------------------------------------


class InningTeamLine(MlbBaseModel):
    """Runs, hits, errors, and LOB for one team in one inning."""

    runs: int | None = None
    hits: int | None = None
    errors: int | None = None
    left_on_base: int | None = None


class LinescoreInning(MlbBaseModel):
    """A single inning in the linescore.

    ``num`` is the 1-based inning number; ``ordinal_num`` is the display
    string (e.g. "1st", "2nd").
    """

    num: int
    ordinal_num: str | None = None
    home: InningTeamLine
    away: InningTeamLine


class LinescoreTeamTotal(MlbBaseModel):
    """Game totals for one team in the linescore."""

    runs: int | None = None
    hits: int | None = None
    errors: int | None = None
    left_on_base: int | None = None
    is_winner: bool | None = None


class LinescoreTeams(MlbBaseModel):
    """Home and away team totals in the linescore."""

    home: LinescoreTeamTotal
    away: LinescoreTeamTotal


class Linescore(MlbBaseModel):
    """Linescore data for a game.

    Contains the inning-by-inning breakdown and current game state
    (current inning, half, and scheduled innings).  Used directly when
    the linescore is embedded inside another response (e.g. live feed).
    """

    current_inning: int | None = None
    current_inning_ordinal: str | None = None
    inning_state: str | None = None
    inning_half: HalfInning | str | None = None
    is_top_inning: bool | None = None
    scheduled_innings: int | None = None
    innings: list[LinescoreInning] = []
    teams: LinescoreTeams | None = None
    note: str | None = None
    balls: int | None = None
    strikes: int | None = None
    outs: int | None = None
    batter: PersonRef | None = None
    on_deck: PersonRef | None = None
    in_hole: PersonRef | None = None
    pitcher: PersonRef | None = None
    on_first: PersonRef | None = None
    on_second: PersonRef | None = None
    on_third: PersonRef | None = None


class LinescoreResponse(BaseResponse, Linescore):
    """Response from ``/api/v1/game/{gamePk}/linescore``."""


# ---------------------------------------------------------------------------
# Boxscore
# ---------------------------------------------------------------------------


class BoxscoreInfoField(MlbBaseModel):
    """A single label/value field within a boxscore info section."""

    label: str | None = None
    value: str | None = None


class BoxscoreInfo(MlbBaseModel):
    """A titled section of boxscore info (e.g. BATTING, FIELDING).

    Each section has a title and a list of label/value fields describing
    notable events (e.g. "2B: Player Name (5, line drive)").
    """

    title: str | None = None
    field_list: list[BoxscoreInfoField] = []


class PlayerGameStats(MlbBaseModel):
    """Batting/pitching/fielding stats for a player in a game context.

    Stats are stored as dicts because the exact fields vary by stat group
    and the API does not guarantee a fixed schema.
    """

    batting: dict[str, StatValue] = {}
    pitching: dict[str, StatValue] = {}
    fielding: dict[str, StatValue] = {}


class PlayerGameStatus(MlbBaseModel):
    """Player in-game status flags."""

    is_current_batter: bool | None = None
    is_current_pitcher: bool | None = None
    is_on_bench: bool | None = None
    is_substitute: bool | None = None


class BoxscorePlayer(MlbBaseModel):
    """An individual player's boxscore entry.

    Contains the player reference, position, jersey number, and
    both game-level and season-level stats.
    """

    person: PersonRef
    jersey_number: str | None = None
    position: PositionRef | None = None
    parent_team_id: TeamId | None = None
    stats: PlayerGameStats | None = None
    season_stats: PlayerGameStats | None = None
    game_status: PlayerGameStatus | None = None
    status: CodeDescription | None = None
    all_positions: list[PositionRef] | None = None
    batting_order: str | None = None


class BoxscoreTeamStats(MlbBaseModel):
    """Team-level aggregate stats (batting, pitching, fielding)."""

    batting: dict[str, StatValue] | None = None
    pitching: dict[str, StatValue] | None = None
    fielding: dict[str, StatValue] | None = None


class BoxscoreTeam(MlbBaseModel):
    """One team's boxscore data.

    Players are stored in a dict keyed by ``"ID{playerId}"``.
    The ``batters``, ``pitchers``, ``bench``, and ``bullpen`` fields
    contain player IDs that can be resolved to ``BoxscorePlayer``
    objects using the helper properties.
    """

    team: Team
    team_stats: BoxscoreTeamStats | None = None
    players: dict[str, BoxscorePlayer] = {}
    batters: list[PersonId] = []
    pitchers: list[PersonId] = []
    bench: list[PersonId] = []
    bullpen: list[PersonId] = []
    batting_order: list[PersonId] = []
    info: list[BoxscoreInfo] = []
    note: list[BoxscoreInfoField] = []

    def _resolve_ids(
        self,
        ids: list[PersonId],
    ) -> list[BoxscorePlayer]:
        """Resolve a list of player IDs to BoxscorePlayer objects."""
        return [self.players[key] for pid in ids if (key := f"ID{pid}") in self.players]

    @property
    def batter_players(self) -> list[BoxscorePlayer]:
        """Resolve batter IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.batters)

    @property
    def pitcher_players(self) -> list[BoxscorePlayer]:
        """Resolve pitcher IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.pitchers)

    @property
    def bench_players(self) -> list[BoxscorePlayer]:
        """Resolve bench IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.bench)

    @property
    def bullpen_players(self) -> list[BoxscorePlayer]:
        """Resolve bullpen IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.bullpen)

    @property
    def batting_order_players(self) -> list[BoxscorePlayer]:
        """Resolve batting_order IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.batting_order)


class BoxscoreTeams(MlbBaseModel):
    """Away and home team boxscore data."""

    away: BoxscoreTeam
    home: BoxscoreTeam


class BoxscoreOfficial(MlbBaseModel):
    """A game official (umpire) in the boxscore."""

    official: PersonRef | None = None
    official_type: str | None = None


class Boxscore(MlbBaseModel):
    """Boxscore data for a game.

    Contains team-level and player-level statistics, batting orders,
    game officials, and supplementary info sections.  Used directly
    when the boxscore is embedded inside another response (e.g. live feed).
    """

    teams: BoxscoreTeams
    officials: list[BoxscoreOfficial] = []
    info: list[BoxscoreInfo] = []
    pitching_notes: list[str] = []
    top_performers: list[MlbBaseModel] = []


class BoxscoreResponse(BaseResponse, Boxscore):
    """Response from ``/api/v1/game/{gamePk}/boxscore``."""
