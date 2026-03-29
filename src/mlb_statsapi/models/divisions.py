"""Division models.

Endpoint: ``/api/v1/divisions``

Divisions group teams within a league (e.g. AL East, NL West).
"""

from __future__ import annotations

from mlb_statsapi.models._base import (
    DivisionId,
    LeagueId,
    ListResponse,
    Ref,
    SportId,
)


class Division(Ref[DivisionId]):
    """A division within a league.

    Inherits ``id``, ``name``, and ``link`` from ``Ref[DivisionId]``.

    Example division IDs:
    - ``200`` — AL West
    - ``201`` — AL East
    - ``202`` — AL Central
    - ``203`` — NL West
    - ``204`` — NL East
    - ``205`` — NL Central
    """

    season: int | None = None
    name_short: str | None = None
    abbreviation: str | None = None
    league: Ref[LeagueId] | None = None
    sport: Ref[SportId] | None = None
    has_wildcard: bool | None = None
    sort_order: int | None = None
    num_playoff_teams: int | None = None
    active: bool | None = None


class DivisionsResponse(ListResponse[Division], items_field="divisions"):
    """Response from ``/api/v1/divisions``."""

    divisions: list[Division]
