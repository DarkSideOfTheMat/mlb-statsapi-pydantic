"""Venue models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, MlbBaseModel


class Venue(MlbBaseModel):
    id: int
    name: str | None = None
    link: str
    active: bool | None = None
    season: int | None = None


class VenuesResponse(BaseResponse):
    venues: list[Venue]
