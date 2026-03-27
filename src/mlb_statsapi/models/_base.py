"""Base models and common reference types for MLB Stats API responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


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
