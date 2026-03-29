"""Sport models.

Endpoint: ``/api/v1/sports``

A sport represents a level of play within professional baseball
(e.g. MLB, AAA, AA, High-A, Single-A, Rookie).
"""

from __future__ import annotations

from mlb_statsapi.models._base import ListResponse, Ref, SportId


class Sport(Ref[SportId]):
    """A level of play within professional baseball.

    Inherits ``id``, ``name``, and ``link`` from ``Ref[SportId]``.

    Common sport IDs:
    - ``1`` — Major League Baseball (MLB)
    - ``11`` — Triple-A (AAA)
    - ``12`` — Double-A (AA)
    - ``13`` — High-A
    - ``14`` — Single-A
    - ``16`` — Rookie
    """

    code: str | None = None
    abbreviation: str | None = None
    sort_order: int | None = None
    active_status: bool | None = None
    season_state: str | None = None
    affiliated: bool | None = None


class SportsResponse(ListResponse[Sport], items_field="sports"):
    """Response from ``/api/v1/sports``."""

    sports: list[Sport]
