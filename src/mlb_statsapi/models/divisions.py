"""Division models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class Division(MlbBaseModel):
    id: int
    name: str
    season: int
    name_short: str
    link: str
    abbreviation: str
    league: IdNameLink
    sport: IdNameLink
    has_wildcard: bool
    sort_order: int
    num_playoff_teams: int
    active: bool


class DivisionsResponse(BaseResponse):
    divisions: list[Division]
