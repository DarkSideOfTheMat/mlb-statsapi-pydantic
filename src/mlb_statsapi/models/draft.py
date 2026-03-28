"""Draft models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    ApiLink,
    BaseResponse,
    CodeDescription,
    IdNameLink,
    MlbBaseModel,
    PositionRef,
)


class DraftPerson(MlbBaseModel):
    id: int | None = None
    full_name: str | None = None
    link: ApiLink | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: datetime.date | None = None
    draft_year: int | None = None
    primary_position: PositionRef | None = None


class DraftSchool(MlbBaseModel):
    name: str | None = None
    school_class: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class DraftHome(MlbBaseModel):
    city: str | None = None
    state: str | None = None
    country: str | None = None


class DraftPick(MlbBaseModel):
    bis_player_id: int | None = None
    pick_round: str | None = None
    pick_number: int | None = None
    display_pick_number: int | None = None
    round_pick_number: int | None = None
    rank: int | None = None
    pick_value: str | None = None
    signing_bonus: str | None = None
    scouting_report: str | None = None
    blurb: str | None = None
    headshot_link: str | None = None
    person: DraftPerson | None = None
    team: IdNameLink | None = None
    draft_type: CodeDescription | None = None
    home: DraftHome | None = None
    school: DraftSchool | None = None
    is_drafted: bool | None = None
    is_pass: bool | None = None
    year: int | None = None

    @property
    def pick_value_amount(self) -> float | None:
        """Parse pick_value string like '9200000.00' into float."""
        if not self.pick_value:
            return None
        try:
            return float(self.pick_value)
        except ValueError:
            return None

    @property
    def signing_bonus_amount(self) -> float | None:
        """Parse signing_bonus string like '9200000.00' into float."""
        if not self.signing_bonus:
            return None
        try:
            return float(self.signing_bonus)
        except ValueError:
            return None


class DraftRound(MlbBaseModel):
    round: str | None = None
    picks: list[DraftPick] = []


class Draft(MlbBaseModel):
    draft_year: int | None = None
    rounds: list[DraftRound] = []


class DraftResponse(BaseResponse):
    drafts: Draft | None = None
