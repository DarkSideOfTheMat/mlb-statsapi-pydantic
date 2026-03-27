"""Schedule models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class GameStatus(MlbBaseModel):
    abstract_game_state: str
    coded_game_state: str | None = None
    detailed_state: str
    status_code: str | None = None
    start_time_tbd: bool | None = None
    abstract_game_code: str | None = None


class LeagueRecord(MlbBaseModel):
    wins: int
    losses: int
    pct: str
    ties: int | None = None


class ScheduleTeamInfo(MlbBaseModel):
    team: IdNameLink
    league_record: LeagueRecord | None = None
    score: int | None = None
    is_winner: bool | None = None
    split_squad: bool | None = None
    series_number: int | None = None


class ScheduleTeams(MlbBaseModel):
    away: ScheduleTeamInfo
    home: ScheduleTeamInfo


class ScheduleGame(MlbBaseModel):
    game_pk: int
    game_guid: str | None = None
    link: str
    game_type: str
    season: str
    game_date: str | None = None
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
    date: str
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
