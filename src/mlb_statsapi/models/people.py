"""People / player models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    ApiLink,
    CodeDescription,
    ListResponse,
    MlbBaseModel,
    PersonId,
    PositionRef,
)


class Person(MlbBaseModel):
    id: PersonId
    full_name: str
    link: ApiLink
    first_name: str | None = None
    last_name: str | None = None
    primary_number: str | None = None
    birth_date: datetime.date | None = None
    current_age: int | None = None
    birth_city: str | None = None
    birth_state_province: str | None = None
    birth_country: str | None = None
    height: str | None = None
    weight: int | None = None
    active: bool
    primary_position: PositionRef | None = None
    use_name: str | None = None
    use_last_name: str | None = None
    boxscore_name: str | None = None
    nick_name: str | None = None
    gender: str | None = None
    is_player: bool | None = None
    is_verified: bool | None = None
    pronunciation: str | None = None
    mlb_debut_date: datetime.date | None = None
    bat_side: CodeDescription | None = None
    pitch_hand: CodeDescription | None = None
    strike_zone_top: float | None = None
    strike_zone_bottom: float | None = None
    name_first_last: str | None = None
    name_slug: str | None = None

    @property
    def height_inches(self) -> int | None:
        """Parse height string like '6\\' 2\"' into total inches."""
        if not self.height:
            return None
        try:
            parts = self.height.replace('"', "").split("' ")
            return int(parts[0]) * 12 + int(parts[1]) if len(parts) == 2 else None
        except (ValueError, IndexError):
            return None


class PeopleResponse(ListResponse[Person], items_field="people"):
    people: list[Person]
