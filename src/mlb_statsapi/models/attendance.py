"""Attendance models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class AttendanceGame(MlbBaseModel):
    game_pk: int | None = None
    link: str | None = None


class AttendanceRecord(MlbBaseModel):
    openings_total: int | None = None
    openings_total_away: int | None = None
    openings_total_home: int | None = None
    openings_total_lost: int | None = None
    games_total: int | None = None
    games_away_total: int | None = None
    games_home_total: int | None = None
    year: int | None = None
    attendance_average_away: int | None = None
    attendance_average_home: int | None = None
    attendance_average_ytd: int | None = None
    attendance_high: int | None = None
    attendance_high_date: str | None = None
    attendance_high_game: AttendanceGame | None = None
    attendance_low: int | None = None
    attendance_low_date: str | None = None
    attendance_low_game: AttendanceGame | None = None
    attendance_opening_average: int | None = None
    attendance_total: int | None = None
    attendance_total_away: int | None = None
    attendance_total_home: int | None = None
    game_type: MlbBaseModel | None = None
    team: IdNameLink | None = None


class AttendanceResponse(BaseResponse):
    records: list[AttendanceRecord] = []
    aggregate_totals: AttendanceRecord | None = None
