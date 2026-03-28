"""Stats and leaders models."""

from __future__ import annotations

from mlb_statsapi.models._base import (
    BaseResponse,
    IdNameLink,
    MlbBaseModel,
    PersonRef,
)
from mlb_statsapi.models.enums import StatGroup as StatGroupEnum

# Backwards-compatible alias
LeaderPersonRef = PersonRef


class GameTypeRef(MlbBaseModel):
    """gameType can be a string or {id, description} object."""

    id: str
    description: str | None = None


class LeaderEntry(MlbBaseModel):
    rank: int
    value: str
    team: IdNameLink | None = None
    league: IdNameLink | None = None
    person: PersonRef
    sport: IdNameLink | None = None
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
    team: IdNameLink | None = None
    player: IdNameLink | None = None
    sport: IdNameLink | None = None
    game_type: GameTypeRef | str | None = None


class StatGroup(MlbBaseModel):
    display_name: str | None = None
    group: str | None = None
    type: str | None = None
    splits: list[StatSplit] = []


class StatsResponse(BaseResponse):
    league_leaders: list[LeaderCategory] = []
    stats: list[StatGroup] = []
