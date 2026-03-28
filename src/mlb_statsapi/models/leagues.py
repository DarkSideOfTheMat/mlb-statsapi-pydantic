"""League models."""

from __future__ import annotations

from mlb_statsapi.models._base import ApiLink, LeagueId, ListResponse, MlbBaseModel


class League(MlbBaseModel):
    id: LeagueId
    name: str | None = None
    link: ApiLink
    abbreviation: str | None = None
    name_short: str | None = None
    season_state: str | None = None
    has_wild_card: bool | None = None
    has_split_season: bool | None = None
    num_games: int | None = None
    has_playoff_points: bool | None = None
    num_teams: int | None = None
    num_wildcard_teams: int | None = None


class LeaguesResponse(ListResponse[League], items_field="leagues"):
    leagues: list[League]
