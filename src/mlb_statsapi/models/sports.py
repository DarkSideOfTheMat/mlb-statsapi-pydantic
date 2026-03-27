"""Sport models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, MlbBaseModel


class Sport(MlbBaseModel):
    id: int
    code: str
    link: str
    name: str
    abbreviation: str
    sort_order: int
    active_status: bool


class SportsResponse(BaseResponse):
    sports: list[Sport]
