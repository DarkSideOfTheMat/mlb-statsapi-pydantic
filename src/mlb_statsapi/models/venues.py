"""Venue models.

Endpoint: ``/api/v1/venues``

Venues represent ballparks and stadiums where games are played.
"""

from __future__ import annotations

from mlb_statsapi.models._base import ListResponse, MlbBaseModel, Ref, VenueId


class VenueTimeZone(MlbBaseModel):
    """Time zone information for a venue."""

    id: str | None = None
    offset: int | None = None
    tz: str | None = None


class VenueLocation(MlbBaseModel):
    """Geographic location of a venue."""

    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    state_abbrev: str | None = None
    postal_code: str | None = None
    country: str | None = None
    phone: str | None = None
    default_coordinates: MlbBaseModel | None = None


class VenueFieldInfo(MlbBaseModel):
    """Field dimensions and surface information."""

    capacity: int | None = None
    turf_type: str | None = None
    roof_type: str | None = None
    left_line: int | None = None
    left: int | None = None
    left_center: int | None = None
    center: int | None = None
    right_center: int | None = None
    right: int | None = None
    right_line: int | None = None


class Venue(Ref[VenueId]):
    """A ballpark or stadium.

    Inherits ``id``, ``name``, and ``link`` from ``Ref[VenueId]``.

    Common venue IDs:
    - ``3313`` — Yankee Stadium
    - ``15`` — Chase Field
    - ``4`` — Wrigley Field
    - ``2680`` — Dodger Stadium
    - ``31`` — PNC Park
    """

    city: str | None = None
    location: VenueLocation | None = None
    time_zone: VenueTimeZone | None = None
    field_info: VenueFieldInfo | None = None
    active: bool | None = None
    season: str | None = None


class VenuesResponse(ListResponse[Venue], items_field="venues"):
    """Response from ``/api/v1/venues``."""

    venues: list[Venue]
