"""Division models."""

from __future__ import annotations

from mlb_statsapi.models._base import (
    ApiLink,
    DivisionId,
    LeagueId,
    ListResponse,
    MlbBaseModel,
    Ref,
    SportId,
)


class Division(MlbBaseModel):
    id: DivisionId
    name: str
    season: int
    name_short: str
    link: ApiLink
    abbreviation: str
    league: Ref[LeagueId]
    sport: Ref[SportId]
    has_wildcard: bool
    sort_order: int
    num_playoff_teams: int
    active: bool


class DivisionsResponse(ListResponse[Division], items_field="divisions"):
    divisions: list[Division]
