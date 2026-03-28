"""Award models."""

from __future__ import annotations

from mlb_statsapi.models._base import ListResponse, MlbBaseModel, Ref, SportId


class Award(MlbBaseModel):
    id: str
    name: str
    description: str | None = None
    sort_order: int | None = None
    sport: Ref[SportId] | None = None
    active: bool | None = None


class AwardsResponse(ListResponse[Award], items_field="awards"):
    awards: list[Award] = []
