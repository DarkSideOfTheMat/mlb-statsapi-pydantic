"""Draft models.

Endpoint: ``/api/v1/draft/{year}``

The draft endpoint returns pick-by-pick data organized by round,
including prospect information, scouting reports, and signing details.
"""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    ApiLink,
    BaseResponse,
    CodeDescription,
    MlbBaseModel,
    PositionRef,
    Ref,
    TeamId,
)


class DraftPerson(MlbBaseModel):
    """Biographical information for a draft prospect."""

    id: int | None = None
    full_name: str | None = None
    link: ApiLink | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: datetime.date | None = None
    draft_year: int | None = None
    primary_position: PositionRef | None = None
    bat_side: CodeDescription | None = None
    pitch_hand: CodeDescription | None = None
    height: str | None = None
    weight: int | None = None
    current_age: int | None = None
    birth_city: str | None = None
    birth_state_province: str | None = None
    birth_country: str | None = None


class DraftSchool(MlbBaseModel):
    """School information for a draft prospect."""

    name: str | None = None
    school_class: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class DraftHome(MlbBaseModel):
    """Home location of a draft prospect."""

    city: str | None = None
    state: str | None = None
    country: str | None = None


class DraftPick(MlbBaseModel):
    """A single draft pick.

    Contains the pick position, prospect info, scouting report,
    and signing details. The ``pick_value`` and ``signing_bonus``
    fields are strings (e.g. ``"9200000.00"``) — use the
    corresponding properties to get numeric values.
    """

    bis_player_id: int | None = None
    bis_school_id: int | None = None
    draft_player_id: int | None = None
    pick_round: str | None = None
    pick_round_label: str | None = None
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
    team: Ref[TeamId] | None = None
    draft_type: CodeDescription | None = None
    draft_status: CodeDescription | None = None
    home: DraftHome | None = None
    school: DraftSchool | None = None
    is_drafted: bool | None = None
    is_pass: bool | None = None
    was_passed: bool | None = None
    was_last_pick: bool | None = None
    was_selected: bool | None = None
    year: str | None = None
    picked_team_code: str | None = None
    comments: str | None = None

    @property
    def pick_value_amount(self) -> float | None:
        """Parse ``pick_value`` string into float."""
        if not self.pick_value:
            return None
        try:
            return float(self.pick_value)
        except ValueError:
            return None

    @property
    def signing_bonus_amount(self) -> float | None:
        """Parse ``signing_bonus`` string into float."""
        if not self.signing_bonus:
            return None
        try:
            return float(self.signing_bonus)
        except ValueError:
            return None


class DraftRound(MlbBaseModel):
    """A single round of the draft containing multiple picks."""

    round: str | None = None
    picks: list[DraftPick] = []


class Draft(MlbBaseModel):
    """A complete draft with all rounds and picks."""

    draft_year: int | None = None
    rounds: list[DraftRound] = []


class DraftResponse(BaseResponse):
    """Response from ``/api/v1/draft/{year}``."""

    drafts: Draft | None = None
