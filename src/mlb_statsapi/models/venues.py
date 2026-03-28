"""Venue models."""

from __future__ import annotations

from mlb_statsapi.models._base import ApiLink, ListResponse, MlbBaseModel, VenueId


class Venue(MlbBaseModel):
    id: VenueId
    name: str | None = None
    link: ApiLink
    active: bool | None = None
    season: int | None = None


class VenuesResponse(ListResponse[Venue], items_field="venues"):
    venues: list[Venue]
