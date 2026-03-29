"""People / player models.

Endpoint: ``/api/v1/people/{personId}``

People represent players, coaches, umpires, and other personnel.
The ``Person`` model covers the full set of biographical and
career information returned by the API.
"""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    CodeDescription,
    ListResponse,
    PersonRef,
    PositionRef,
    Ref,
    TeamId,
)


class Person(PersonRef):
    """A player, coach, umpire, or other MLB personnel.

    Inherits ``id``, ``full_name``, and ``link`` from ``PersonRef``.

    The API returns varying subsets of fields depending on the endpoint
    and hydrations used. Most fields are optional because a person
    reference in a boxscore will have fewer fields than a full
    ``/api/v1/people/{id}`` response.
    """

    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    use_name: str | None = None
    use_last_name: str | None = None
    boxscore_name: str | None = None
    nick_name: str | None = None
    nick_names: list[str] | None = None
    name_first_last: str | None = None
    first_last_name: str | None = None
    last_first_name: str | None = None
    last_init_name: str | None = None
    init_last_name: str | None = None
    full_fml_name: str | None = None
    full_lfm_name: str | None = None
    name_slug: str | None = None
    name_title: str | None = None
    name_prefix: str | None = None
    name_matrilineal: str | None = None
    primary_number: str | None = None
    birth_date: datetime.date | None = None
    current_age: int | None = None
    birth_city: str | None = None
    birth_state_province: str | None = None
    birth_country: str | None = None
    death_date: datetime.date | None = None
    death_city: str | None = None
    death_state_province: str | None = None
    death_country: str | None = None
    height: str | None = None
    weight: int | None = None
    active: bool | None = None
    primary_position: PositionRef | None = None
    gender: str | None = None
    is_player: bool | None = None
    is_verified: bool | None = None
    is_rookie: bool | None = None
    pronunciation: str | None = None
    phonetic_name: str | None = None
    nationality: str | None = None
    mlb_debut_date: datetime.date | None = None
    last_played_date: datetime.date | None = None
    bat_side: CodeDescription | None = None
    pitch_hand: CodeDescription | None = None
    strike_zone_top: float | None = None
    strike_zone_bottom: float | None = None
    draft_year: int | None = None
    current_team: Ref[TeamId] | None = None
    pitcher: bool | None = None
    fielder: bool | None = None
    batter_pitcher: str | None = None
    note: str | None = None
    alumni_last_season: str | None = None

    @property
    def height_inches(self) -> int | None:
        """Parse height string like ``6' 2"`` into total inches."""
        if not self.height:
            return None
        try:
            parts = self.height.replace('"', "").split("' ")
            return int(parts[0]) * 12 + int(parts[1]) if len(parts) == 2 else None
        except (ValueError, IndexError):
            return None


class PeopleResponse(ListResponse[Person], items_field="people"):
    """Response from ``/api/v1/people/{personId}``."""

    people: list[Person]
