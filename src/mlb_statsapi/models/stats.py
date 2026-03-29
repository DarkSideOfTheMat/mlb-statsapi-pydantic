"""Stats and leaders models.

Endpoints:
- ``/api/v1/stats`` — player and team statistics
- ``/api/v1/stats/leaders`` — league leaders

Statistics are organized by group (hitting, pitching, fielding) and
type (season, career, gameLog, etc.). Leader categories rank players
across a stat within a season.
"""

from __future__ import annotations

from mlb_statsapi.models._base import (
    BaseResponse,
    LeagueId,
    MlbBaseModel,
    PersonId,
    PersonRef,
    Ref,
    SportId,
    TeamId,
)
from mlb_statsapi.models.enums import StatGroup as StatGroupEnum
from mlb_statsapi.models.teams import Team


class GameTypeRef(MlbBaseModel):
    """Game type reference — ``gameType`` can be a string or ``{id, description}``."""

    id: str
    description: str | None = None


class LeaderEntry(MlbBaseModel):
    """A single entry in a league leaders category.

    Includes the player, their rank, stat value, and optional
    team/league/sport context.
    """

    rank: int
    value: str
    team: Team | Ref[TeamId] | None = None
    league: Ref[LeagueId] | None = None
    person: PersonRef
    sport: Ref[SportId] | None = None
    season: str | None = None
    num_teams: int | None = None


class LeaderCategory(MlbBaseModel):
    """A category of league leaders (e.g. home runs, batting average).

    Contains the category name, season, game type, and the ranked
    list of leader entries.
    """

    leader_category: str
    season: str | None = None
    game_type: GameTypeRef | str | None = None
    stat_group: StatGroupEnum | str | None = None
    total_splits: int | None = None
    leaders: list[LeaderEntry] = []


class StatSplit(MlbBaseModel):
    """A single statistical split (e.g. one season's stats for a player).

    The ``stat`` dict contains the actual stat values. Keys vary by
    stat group (hitting stats differ from pitching stats).
    """

    season: str | None = None
    stat: dict[str, int | str | float] | None = None
    team: Ref[TeamId] | None = None
    player: Ref[PersonId] | None = None
    sport: Ref[SportId] | None = None
    game_type: GameTypeRef | str | None = None
    num_teams: int | None = None
    position: MlbBaseModel | None = None


class StatGroup(MlbBaseModel):
    """A group of stat splits (e.g. "season" hitting stats).

    Contains metadata about the stat type and display name,
    plus the list of individual splits.
    """

    display_name: str | None = None
    group: str | None = None
    type: str | None = None
    splits: list[StatSplit] = []
    total_splits: int | None = None
    exemptions: list[MlbBaseModel] = []


class StatsResponse(BaseResponse):
    """Response from ``/api/v1/stats`` and ``/api/v1/stats/leaders``.

    May contain ``stats`` (for stat queries) and/or ``league_leaders``
    (for leader queries), depending on the endpoint called.
    """

    league_leaders: list[LeaderCategory] = []
    stats: list[StatGroup] = []
