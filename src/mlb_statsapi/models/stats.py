"""Stats and leaders models."""

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


class GameTypeRef(MlbBaseModel):
    """gameType can be a string or {id, description} object."""

    id: str
    description: str | None = None


class LeaderEntry(MlbBaseModel):
    rank: int
    value: str
    team: Ref[TeamId] | None = None
    league: Ref[LeagueId] | None = None
    person: PersonRef
    sport: Ref[SportId] | None = None
    season: int | None = None
    num_teams: int | None = None


class LeaderCategory(MlbBaseModel):
    leader_category: str
    season: str | None = None
    game_type: GameTypeRef | str | None = None
    stat_group: StatGroupEnum | str | None = None
    total_splits: int | None = None
    leaders: list[LeaderEntry] = []


class StatSplit(MlbBaseModel):
    season: str | None = None
    stat: dict[str, int | str | float] | None = None
    team: Ref[TeamId] | None = None
    player: Ref[PersonId] | None = None
    sport: Ref[SportId] | None = None
    game_type: GameTypeRef | str | None = None


class StatGroup(MlbBaseModel):
    display_name: str | None = None
    group: str | None = None
    type: str | None = None
    splits: list[StatSplit] = []


class StatsResponse(BaseResponse):
    league_leaders: list[LeaderCategory] = []
    stats: list[StatGroup] = []
