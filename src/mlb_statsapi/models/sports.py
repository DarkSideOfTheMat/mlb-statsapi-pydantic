"""Sport models."""

from __future__ import annotations

from mlb_statsapi.models._base import ApiLink, ListResponse, MlbBaseModel, SportId


class Sport(MlbBaseModel):
    id: SportId
    code: str
    link: ApiLink
    name: str
    abbreviation: str
    sort_order: int
    active_status: bool


class SportsResponse(ListResponse[Sport], items_field="sports"):
    sports: list[Sport]
