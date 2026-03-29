"""Schedule models.

Endpoint: ``/api/v1/schedule``

The schedule endpoint returns games organized by date. Each game includes
team info, status, venue, and various metadata about the series and
doubleheader status.
"""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    ApiLink,
    BaseResponse,
    GamePk,
    GameStatus,
    MlbBaseModel,
    PersonRef,
    Ref,
    VenueId,
    WinLossRecord,
)
from mlb_statsapi.models.enums import (
    DayNight,
    DoubleHeaderCode,
    GameType,
    TiebreakerCode,
)
from mlb_statsapi.models.people import Person
from mlb_statsapi.models.teams import Team
from mlb_statsapi.models.venues import Venue


class ScheduleTeamInfo(MlbBaseModel):
    """Team info within a scheduled game, including record and score."""

    team: Team
    league_record: WinLossRecord | None = None
    score: int | None = None
    is_winner: bool | None = None
    split_squad: bool | None = None
    series_number: int | None = None
    probable_pitcher: Person | PersonRef | None = None


class ScheduleTeams(MlbBaseModel):
    """Away and home team info for a scheduled game."""

    away: ScheduleTeamInfo
    home: ScheduleTeamInfo


class SeriesStatus(MlbBaseModel):
    """Postseason series status for a game."""

    game_number: int | None = None
    total_games: int | None = None
    is_tied: bool | None = None
    is_over: bool | None = None
    result: str | None = None
    description: str | None = None
    short_description: str | None = None
    short_name: str | None = None


class ScheduleGame(MlbBaseModel):
    """A single game within the schedule.

    Contains the core game identity (``game_pk``), participating teams with
    records and scores, game status, and metadata about the series context.
    """

    game_pk: GamePk
    game_guid: str | None = None
    link: ApiLink
    game_type: GameType | str
    season: int | None = None
    game_date: datetime.datetime | None = None
    official_date: datetime.date | None = None
    status: GameStatus
    teams: ScheduleTeams
    venue: Venue | Ref[VenueId]
    day_night: DayNight | str | None = None
    description: str | None = None
    scheduled_innings: int | None = None
    game_number: int | None = None
    double_header: DoubleHeaderCode | str | None = None
    gameday_type: str | None = None
    tiebreaker: TiebreakerCode | str | None = None
    is_tie: bool | None = None
    season_display: str | None = None
    public_facing: bool | None = None
    series_description: str | None = None
    series_game_number: int | None = None
    games_in_series: int | None = None
    series_status: SeriesStatus | None = None
    if_necessary: str | None = None
    if_necessary_description: str | None = None
    game_id: str | None = None
    record_source: str | None = None
    inning_break_length: int | None = None
    reverse_home_away_status: bool | None = None


class ScheduleDate(MlbBaseModel):
    """Games grouped by date."""

    date: datetime.date
    total_items: int | None = None
    total_events: int | None = None
    total_games: int | None = None
    total_games_in_progress: int | None = None
    games: list[ScheduleGame] = []


class ScheduleResponse(BaseResponse):
    """Response from ``/api/v1/schedule``.

    Games are grouped into ``dates``, each containing a list of games
    for that calendar date. Root-level totals aggregate across all dates.
    """

    total_items: int | None = None
    total_events: int | None = None
    total_games: int | None = None
    total_games_in_progress: int | None = None
    dates: list[ScheduleDate] = []
