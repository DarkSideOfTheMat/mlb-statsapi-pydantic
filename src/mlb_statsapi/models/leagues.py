"""League models.

Endpoint: ``/api/v1/league``

Leagues organize play within a sport (e.g. American League, National League,
Cactus League, Grapefruit League).
"""

from __future__ import annotations

from mlb_statsapi.models._base import LeagueId, ListResponse, Ref, SportId


class League(Ref[LeagueId]):
    """A league within a sport.

    Inherits ``id``, ``name``, and ``link`` from ``Ref[LeagueId]``.

    Common league IDs:
    - ``103`` — American League (AL)
    - ``104`` — National League (NL)
    - ``114`` — Cactus League (spring training)
    - ``115`` — Grapefruit League (spring training)
    """

    abbreviation: str | None = None
    name_short: str | None = None
    org_code: str | None = None
    sport: Ref[SportId] | None = None
    season_state: str | None = None
    has_wild_card: bool | None = None
    has_split_season: bool | None = None
    num_games: int | None = None
    has_playoff_points: bool | None = None
    num_teams: int | None = None
    num_wildcard_teams: int | None = None
    has_divisions: bool | None = None
    has_conferences: bool | None = None
    sort_order: int | None = None
    active: bool | None = None
    affiliated: bool | None = None
    season: str | None = None


class LeaguesResponse(ListResponse[League], items_field="leagues"):
    """Response from ``/api/v1/league``."""

    leagues: list[League]
