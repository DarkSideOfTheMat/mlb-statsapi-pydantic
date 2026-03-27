"""People / player models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    BaseResponse,
    CodeDescription,
    MlbBaseModel,
)


class PrimaryPosition(MlbBaseModel):
    code: str
    name: str
    type: str
    abbreviation: str


class Person(MlbBaseModel):
    id: int
    full_name: str
    link: str
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
    primary_position: PrimaryPosition | None = None
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


class PeopleResponse(BaseResponse):
    people: list[Person]
