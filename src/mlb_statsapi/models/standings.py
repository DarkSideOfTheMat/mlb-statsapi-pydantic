"""Standings models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    BaseResponse,
    IdNameLink,
    MlbBaseModel,
    WinLossRecord,
)


class Streak(MlbBaseModel):
    streak_code: str | None = None
    streak_type: str | None = None
    streak_number: int | None = None


# Backwards-compatible aliases
StandingsLeagueRecord = WinLossRecord
SplitRecord = WinLossRecord


class TeamStanding(MlbBaseModel):
    team: IdNameLink
    season: int
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
    league_record: WinLossRecord | None = None
    last_updated: datetime.datetime | None = None


class StandingsRecord(MlbBaseModel):
    standings_type: str
    league: IdNameLink
    division: IdNameLink
    sport: IdNameLink | None = None
    last_updated: datetime.datetime | None = None
    team_records: list[TeamStanding] = []


class StandingsResponse(BaseResponse):
    records: list[StandingsRecord] = []
