"""Draft models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class DraftPerson(MlbBaseModel):
    id: int | None = None
    full_name: str | None = None
    link: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: str | None = None
    draft_year: int | None = None
    primary_position: MlbBaseModel | None = None


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
    draft_type: MlbBaseModel | None = None
    home: DraftHome | None = None
    school: DraftSchool | None = None
    is_drafted: bool | None = None
    is_pass: bool | None = None
    year: str | None = None


class DraftRound(MlbBaseModel):
    round: str | None = None
    picks: list[DraftPick] = []


class Draft(MlbBaseModel):
    draft_year: int | None = None
    rounds: list[DraftRound] = []


class DraftResponse(BaseResponse):
    drafts: Draft | None = None
