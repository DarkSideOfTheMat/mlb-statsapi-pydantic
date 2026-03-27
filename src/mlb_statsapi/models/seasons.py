"""Season models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import BaseResponse, MlbBaseModel


class Season(MlbBaseModel):
    season_id: str
    has_wildcard: bool | None = None
    pre_season_start_date: datetime.date | None = None
    pre_season_end_date: datetime.date | None = None
    season_start_date: datetime.date | None = None
    spring_start_date: datetime.date | None = None
    spring_end_date: datetime.date | None = None
    regular_season_start_date: datetime.date | None = None
    last_date1st_half: datetime.date | None = None
    all_star_date: datetime.date | None = None
    first_date2nd_half: datetime.date | None = None
    regular_season_end_date: datetime.date | None = None
    post_season_start_date: datetime.date | None = None
    post_season_end_date: datetime.date | None = None
    season_end_date: datetime.date | None = None
    offseason_start_date: datetime.date | None = None
    off_season_end_date: datetime.date | None = None


class SeasonsResponse(BaseResponse):
    seasons: list[Season]
