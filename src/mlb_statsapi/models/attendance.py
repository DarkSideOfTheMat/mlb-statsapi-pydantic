"""Attendance models.

Endpoint: ``/api/v1/attendance``

Attendance records track game-by-game and aggregate attendance
figures for teams across a season.
"""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    ApiLink,
    BaseResponse,
    GamePk,
    MlbBaseModel,
    Ref,
    TeamId,
)
from mlb_statsapi.models.stats import GameTypeRef


class AttendanceGame(MlbBaseModel):
    """Reference to a specific game for attendance records."""

    game_pk: GamePk | None = None
    link: ApiLink | None = None


class AttendanceRecord(MlbBaseModel):
    """Attendance data for a team in a season.

    Contains counts for openings (opening day games), total games,
    and various attendance statistics including highs, lows, and
    averages for home, away, and combined.
    """

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
    attendance_high_date: datetime.datetime | None = None
    attendance_high_game: AttendanceGame | None = None
    attendance_low: int | None = None
    attendance_low_date: datetime.datetime | None = None
    attendance_low_game: AttendanceGame | None = None
    attendance_opening_average: int | None = None
    attendance_total: int | None = None
    attendance_total_away: int | None = None
    attendance_total_home: int | None = None
    game_type: GameTypeRef | None = None
    team: Ref[TeamId] | None = None


class AttendanceResponse(BaseResponse):
    """Response from ``/api/v1/attendance``.

    Contains per-team records and optional aggregate totals
    across all teams.
    """

    records: list[AttendanceRecord] = []
    aggregate_totals: AttendanceRecord | None = None
