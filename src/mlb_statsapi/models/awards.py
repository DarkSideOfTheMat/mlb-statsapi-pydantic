"""Award models.

Endpoint: ``/api/v1/awards``

Awards represent MLB honors such as MVP, Cy Young, Rookie of the Year,
Gold Glove, Silver Slugger, etc.
"""

from __future__ import annotations

from mlb_statsapi.models._base import (
    LeagueId,
    ListResponse,
    MlbBaseModel,
    PersonRef,
    Ref,
    SportId,
    TeamId,
)


class AwardWinner(MlbBaseModel):
    """An individual award winner or nominee.

    Contains the person, team, and ranking information for a single
    award result within a season.
    """

    person: PersonRef | None = None
    player: PersonRef | None = None
    team: Ref[TeamId] | None = None
    rank: str | None = None
    award_date: str | None = None
    season: str | None = None


class AwardResult(MlbBaseModel):
    """Award results for a specific season."""

    season_id: int | None = None
    winners: list[AwardWinner] = []


class Award(MlbBaseModel):
    """An MLB award type.

    Examples: MVP, Cy Young, Rookie of the Year, Gold Glove,
    Silver Slugger, Manager of the Year.
    """

    id: str
    name: str
    description: str | None = None
    short_name: str | None = None
    sort_order: int | None = None
    sport: Ref[SportId] | None = None
    league: Ref[LeagueId] | None = None
    active: bool | None = None
    notes: str | None = None
    date: str | None = None
    season: str | None = None
    results: list[AwardResult] = []
    winners: list[AwardWinner] = []


class AwardsResponse(ListResponse[Award], items_field="awards"):
    """Response from ``/api/v1/awards``."""

    awards: list[Award] = []
