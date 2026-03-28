"""Team models."""

from __future__ import annotations

from mlb_statsapi.models._base import (
    ApiLink,
    DivisionId,
    LeagueId,
    ListResponse,
    MlbBaseModel,
    Ref,
    SportId,
    TeamId,
    VenueId,
)


class Team(MlbBaseModel):
    id: TeamId
    name: str
    link: ApiLink
    season: int | None = None
    venue: Ref[VenueId]
    spring_venue: Ref[VenueId] | None = None
    team_code: str | None = None
    file_code: str | None = None
    abbreviation: str
    team_name: str
    location_name: str | None = None
    first_year_of_play: int | None = None
    league: Ref[LeagueId]
    division: Ref[DivisionId] | None = None
    sport: Ref[SportId]
    short_name: str | None = None
    franchise_name: str | None = None
    club_name: str | None = None
    spring_league: Ref[LeagueId] | None = None
    all_star_status: str | None = None
    active: bool


class TeamsResponse(ListResponse[Team], items_field="teams"):
    teams: list[Team]
