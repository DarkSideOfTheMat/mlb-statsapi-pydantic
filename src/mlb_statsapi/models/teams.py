"""Team models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class Team(MlbBaseModel):
    id: int
    name: str
    link: str
    season: int | None = None
    venue: IdNameLink
    spring_venue: IdNameLink | None = None
    team_code: str | None = None
    file_code: str | None = None
    abbreviation: str
    team_name: str
    location_name: str | None = None
    first_year_of_play: str | None = None
    league: IdNameLink
    division: IdNameLink | None = None
    sport: IdNameLink
    short_name: str | None = None
    franchise_name: str | None = None
    club_name: str | None = None
    spring_league: IdNameLink | None = None
    all_star_status: str | None = None
    active: bool


class TeamsResponse(BaseResponse):
    teams: list[Team]
