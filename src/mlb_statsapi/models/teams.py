"""Team models.

Endpoint: ``/api/v1/teams``

Teams represent MLB franchises and their affiliates. Each team
includes references to its venue, league, division, and sport.
"""

from __future__ import annotations

from mlb_statsapi.models._base import (
    DivisionId,
    LeagueId,
    ListResponse,
    Ref,
    SportId,
    TeamId,
    VenueId,
)
from mlb_statsapi.models.divisions import Division
from mlb_statsapi.models.leagues import League
from mlb_statsapi.models.sports import Sport
from mlb_statsapi.models.venues import Venue


class Team(Ref[TeamId]):
    """An MLB team or affiliate.

    Inherits ``id``, ``name``, and ``link`` from ``Ref[TeamId]``.

    The API provides multiple name variants for different display contexts:
    - ``name`` — full display name (e.g. "New York Yankees")
    - ``team_name`` — team portion (e.g. "Yankees")
    - ``short_name`` — shortened form (e.g. "NY Yankees")
    - ``franchise_name`` — franchise (e.g. "New York")
    - ``club_name`` — club portion (e.g. "Yankees")
    - ``location_name`` — city/location (e.g. "New York")

    When used as a hydrated reference (e.g. in schedule responses with
    ``?hydrate=team``), the full team data is populated. When used as
    a plain reference, only ``id``, ``name``, and ``link`` are present.
    """

    season: int | None = None
    venue: Venue | Ref[VenueId] | None = None
    spring_venue: Ref[VenueId] | None = None
    team_code: str | None = None
    file_code: str | None = None
    abbreviation: str | None = None
    team_name: str | None = None
    location_name: str | None = None
    first_year_of_play: str | None = None
    league: League | Ref[LeagueId] | None = None
    division: Division | Ref[DivisionId] | None = None
    sport: Sport | Ref[SportId] | None = None
    short_name: str | None = None
    franchise_name: str | None = None
    club_name: str | None = None
    spring_league: Ref[LeagueId] | None = None
    all_star_status: str | None = None
    active: bool | None = None
    parent_org_id: int | None = None
    parent_org_name: str | None = None
    league_id: int | None = None


class TeamsResponse(ListResponse[Team], items_field="teams"):
    """Response from ``/api/v1/teams``."""

    teams: list[Team]
