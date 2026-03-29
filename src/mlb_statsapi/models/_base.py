"""Base models and common reference types for MLB Stats API responses."""

from __future__ import annotations

from typing import Any, ClassVar, Generic, NewType, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from mlb_statsapi.models.enums import (
    AbstractGameState,
    CodedGameState,
    PositionType,
)

# ---------------------------------------------------------------------------
# Semantic ID types — use these instead of bare ``int`` for domain clarity
# ---------------------------------------------------------------------------

PersonId = NewType("PersonId", int)
TeamId = NewType("TeamId", int)
GamePk = NewType("GamePk", int)
SportId = NewType("SportId", int)
LeagueId = NewType("LeagueId", int)
DivisionId = NewType("DivisionId", int)
VenueId = NewType("VenueId", int)
ApiLink = NewType("ApiLink", str)
"""An API endpoint path, e.g. ``/api/v1/people/660271``."""

# TypeVar for the generic Ref model
IdT = TypeVar("IdT", bound=int)

# TypeVar for the generic ListResponse model
T = TypeVar("T")


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


class ListResponse(BaseResponse, Generic[T]):
    """Generic base for API responses that wrap a list of items.

    Subclasses define their own field (e.g. ``sports``, ``teams``) and
    pass ``items_field`` to provide uniform access via the ``items`` property.

    Example::

        class SportsResponse(ListResponse[Sport], items_field="sports"):
            sports: list[Sport] = []

        resp.items  # -> list[Sport], same as resp.sports
    """

    _items_field: ClassVar[str] = ""

    def __init_subclass__(cls, *, items_field: str = "", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if items_field:
            cls._items_field = items_field

    @property
    def items(self) -> list[T]:
        """Access the wrapped list regardless of the field name."""
        return getattr(self, self._items_field, [])


class Ref(MlbBaseModel, Generic[IdT]):
    """Generic ``{id, name, link}`` reference with a typed ID.

    The MLB API uses this pattern everywhere to reference entities:
    teams, venues, leagues, divisions, sports, etc. The generic
    parameter gives each reference an explicit ID type::

        team: Ref[TeamId]       # team.id is TeamId (not bare int)
        venue: Ref[VenueId]     # venue.id is VenueId
        league: Ref[LeagueId]   # league.id is LeagueId

    ``name`` is optional because some refs (e.g. ``springVenue``) omit it.

    Domain models (Team, Venue, etc.) inherit from ``Ref`` so that
    ``isinstance(team, Ref)`` is always ``True``. When the API returns
    hydrated data, the extra fields are populated; otherwise they are ``None``.
    """

    id: IdT
    name: str | None = None
    link: ApiLink

    @property
    def is_hydrated(self) -> bool:
        """Whether this object has data beyond the basic ref fields (id/name/link)."""
        return bool(self.model_extra) or any(
            v is not None
            for k, v in self.__dict__.items()
            if k not in ("id", "name", "link")
        )


# Backwards-compatible alias — prefer ``Ref[TeamId]`` etc. in new code
IdNameLink = Ref[int]


class CodeDescription(MlbBaseModel):
    """The {code, description} pattern used by batSide, pitchHand, etc."""

    code: str
    description: str


class PersonRef(MlbBaseModel):
    """Lightweight person reference (id, fullName, link).

    Used throughout the API for pitchers, batters, umpires, etc.
    Unlike ``Ref``, uses ``fullName`` (not ``name``) and link is optional.

    The ``Person`` model inherits from ``PersonRef`` so that
    ``isinstance(person, PersonRef)`` is always ``True``.
    """

    id: PersonId
    full_name: str | None = None
    link: ApiLink | None = None

    @property
    def is_hydrated(self) -> bool:
        """Whether this object has data beyond the basic ref fields."""
        return bool(self.model_extra) or any(
            v is not None
            for k, v in self.__dict__.items()
            if k not in ("id", "full_name", "link")
        )


class PositionRef(MlbBaseModel):
    """Position reference (code, name, type, abbreviation).

    Uses ``code`` as the key (not ``id``), so this is *not* a Ref.
    """

    code: str
    name: str | None = None
    type: PositionType | str | None = None
    abbreviation: str | None = None


class WinLossRecord(MlbBaseModel):
    """Win/loss record with optional pct, ties, and type."""

    wins: int
    losses: int
    pct: str | None = None
    ties: int | None = None
    type: str | None = None

    @property
    def win_pct(self) -> float | None:
        """Parse pct string like '.512' into float."""
        if self.pct is None:
            return None
        try:
            return float(self.pct)
        except ValueError:
            return None


class GameStatus(MlbBaseModel):
    """Game status — union of fields from schedule and live-feed responses."""

    abstract_game_state: AbstractGameState | str | None = None
    coded_game_state: CodedGameState | str | None = None
    detailed_state: str | None = None
    status_code: str | None = None
    start_time_tbd: bool | None = None
    abstract_game_code: AbstractGameState | str | None = None
