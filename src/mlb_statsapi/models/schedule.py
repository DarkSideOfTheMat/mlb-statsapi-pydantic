"""Schedule models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    BaseResponse,
    GamePk,
    GameStatus,
    IdNameLink,
    MlbBaseModel,
    WinLossRecord,
)
from mlb_statsapi.models.enums import GameType

# Backwards-compatible alias
LeagueRecord = WinLossRecord


class ScheduleTeamInfo(MlbBaseModel):
    team: IdNameLink
    league_record: WinLossRecord | None = None
    score: int | None = None
    is_winner: bool | None = None
    split_squad: bool | None = None
    series_number: int | None = None


class ScheduleTeams(MlbBaseModel):
    away: ScheduleTeamInfo
    home: ScheduleTeamInfo


class ScheduleGame(MlbBaseModel):
    game_pk: GamePk
    game_guid: str | None = None
    link: str
    game_type: GameType | str
    season: int
    game_date: datetime.datetime | None = None
    official_date: datetime.date | None = None
    status: GameStatus
    teams: ScheduleTeams
    venue: IdNameLink
    day_night: str | None = None
    scheduled_innings: int | None = None
    game_number: int | None = None
    double_header: str | None = None
    tiebreaker: str | None = None
    is_tie: bool | None = None
    season_display: str | None = None
    public_facing: bool | None = None


class ScheduleDate(MlbBaseModel):
    date: datetime.date
    total_items: int | None = None
    total_events: int | None = None
    total_games: int | None = None
    total_games_in_progress: int | None = None
    games: list[ScheduleGame] = []


class ScheduleResponse(BaseResponse):
    total_items: int | None = None
    total_events: int | None = None
    total_games: int | None = None
    total_games_in_progress: int | None = None
    dates: list[ScheduleDate] = []
