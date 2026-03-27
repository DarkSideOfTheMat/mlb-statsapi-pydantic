"""Standings models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class Streak(MlbBaseModel):
    streak_code: str | None = None
    streak_type: str | None = None
    streak_number: int | None = None


class StandingsLeagueRecord(MlbBaseModel):
    wins: int
    losses: int
    pct: str
    ties: int | None = None


class SplitRecord(MlbBaseModel):
    wins: int
    losses: int
    type: str
    pct: str


class TeamStanding(MlbBaseModel):
    team: IdNameLink
    season: str
    streak: Streak | None = None
    clinch_indicator: str | None = None
    division_rank: str | None = None
    league_rank: str | None = None
    sport_rank: str | None = None
    games_played: int | None = None
    games_back: str | None = None
    wild_card_games_back: str | None = None
    league_games_back: str | None = None
    spring_league_games_back: str | None = None
    sport_games_back: str | None = None
    division_games_back: str | None = None
    conference_games_back: str | None = None
    league_record: StandingsLeagueRecord | None = None
    last_updated: str | None = None


class StandingsRecord(MlbBaseModel):
    standings_type: str
    league: IdNameLink
    division: IdNameLink
    sport: IdNameLink | None = None
    last_updated: str | None = None
    team_records: list[TeamStanding] = []


class StandingsResponse(BaseResponse):
    records: list[StandingsRecord] = []
