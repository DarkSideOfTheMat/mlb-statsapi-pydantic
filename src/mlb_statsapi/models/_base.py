"""Base models and common reference types for MLB Stats API responses."""

from __future__ import annotations

from typing import NewType

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

PersonId = NewType("PersonId", int)
TeamId = NewType("TeamId", int)
GamePk = NewType("GamePk", int)


class MlbBaseModel(BaseModel):
    """Base for all MLB Stats API models.

    - Accepts camelCase (API) or snake_case (Python) field names
    - Allows extra fields so new API additions don't break parsing
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        alias_generator=to_camel,
    )


class BaseResponse(MlbBaseModel):
    """Root response wrapper — every API response includes copyright."""

    copyright: str


class IdNameLink(MlbBaseModel):
    """Ubiquitous {id, name, link} reference pattern.

    Used for teams, venues, leagues, divisions, and people references.
    ``name`` is optional because some refs (e.g. springVenue) omit it.
    """

    id: int
    name: str | None = None
    link: str


class CodeDescription(MlbBaseModel):
    """The {code, description} pattern used by batSide, pitchHand, etc."""

    code: str
    description: str


class PersonRef(MlbBaseModel):
    """Lightweight person reference (id, fullName, link).

    Used throughout the API for pitchers, batters, umpires, etc.
    """

    id: PersonId
    full_name: str | None = None
    link: str | None = None


class PositionRef(MlbBaseModel):
    """Position reference (code, name, type, abbreviation).

    Uses ``code`` as the key (not ``id``), so this is *not* an IdNameLink.
    """

    code: str
    name: str | None = None
    type: str | None = None
    abbreviation: str | None = None


class WinLossRecord(MlbBaseModel):
    """Win/loss record with optional pct, ties, and type."""

    wins: int
    losses: int
    pct: str | None = None
    ties: int | None = None
    type: str | None = None


class GameStatus(MlbBaseModel):
    """Game status — union of fields from schedule and live-feed responses."""

    abstract_game_state: str | None = None
    coded_game_state: str | None = None
    detailed_state: str | None = None
    status_code: str | None = None
    start_time_tbd: bool | None = None
    abstract_game_code: str | None = None
