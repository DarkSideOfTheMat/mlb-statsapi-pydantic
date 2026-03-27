"""Award models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class Award(MlbBaseModel):
    id: str
    name: str
    description: str | None = None
    sort_order: int | None = None
    sport: IdNameLink | None = None
    active: bool | None = None


class AwardsResponse(BaseResponse):
    awards: list[Award] = []
