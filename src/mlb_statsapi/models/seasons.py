"""Season models.

Endpoint: ``/api/v1/seasons``

Seasons define the calendar structure of a baseball year, including
spring training, regular season, all-star break, and postseason dates.
"""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import ListResponse, MlbBaseModel


class Season(MlbBaseModel):
    """A season's calendar structure with all key date boundaries.

    The season is divided into phases:
    - Pre-season and spring training
    - Regular season (first half, all-star break, second half)
    - Postseason
    - Off-season
    """

    season_id: int
    has_wildcard: bool | None = None
    pre_season_start_date: datetime.date | None = None
    pre_season_end_date: datetime.date | None = None
    season_start_date: datetime.date | None = None
    season_end_date: datetime.date | None = None
    spring_start_date: datetime.date | None = None
    spring_end_date: datetime.date | None = None
    regular_season_start_date: datetime.date | None = None
    regular_season_end_date: datetime.date | None = None
    last_date1st_half: datetime.date | None = None
    all_star_date: datetime.date | None = None
    first_date2nd_half: datetime.date | None = None
    post_season_start_date: datetime.date | None = None
    post_season_end_date: datetime.date | None = None
    off_season_start_date: datetime.date | None = None
    off_season_end_date: datetime.date | None = None
    number_of_games: int | None = None
    olympics_participation: bool | None = None
    ties_in_use: bool | None = None
    conferences_in_use: bool | None = None
    divisions_in_use: bool | None = None
    qualifier_plate_appearances: float | None = None
    qualifier_outs_pitched: float | None = None
    qualifier_innings_pitched: float | None = None
    season_level_gameday_type: str | None = None
    game_level_gameday_type: str | None = None


class SeasonsResponse(ListResponse[Season], items_field="seasons"):
    """Response from ``/api/v1/seasons``."""

    seasons: list[Season]
