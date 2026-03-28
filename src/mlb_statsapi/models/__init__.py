"""Pydantic models for MLB Stats API responses."""

from mlb_statsapi.models._base import (
    ApiLink,
    BaseResponse,
    CodeDescription,
    GamePk,
    GameStatus,
    IdNameLink,
    MlbBaseModel,
    PersonId,
    PersonRef,
    PositionRef,
    TeamId,
    WinLossRecord,
)
from mlb_statsapi.models.attendance import AttendanceRecord, AttendanceResponse
from mlb_statsapi.models.awards import Award, AwardsResponse
from mlb_statsapi.models.divisions import Division, DivisionsResponse
from mlb_statsapi.models.draft import Draft, DraftPick, DraftResponse, DraftRound
from mlb_statsapi.models.enums import (
    AbstractGameState,
    CodedGameState,
    DayNight,
    DetailedGameState,
    DoubleHeaderCode,
    EventType,
    FieldingCredit,
    GameType,
    HalfInning,
    HandCode,
    HitTrajectory,
    PitchCode,
    PitchType,
    PositionAbbreviation,
    PositionType,
    RosterType,
    ScheduleEventType,
    Sky,
    StandingsType,
    StatGroup,
    StatType,
    StreakType,
    TiebreakerCode,
    TransactionType,
    WindDirection,
)
from mlb_statsapi.models.game import BoxscoreResponse, LinescoreResponse
from mlb_statsapi.models.jobs import JobEntry, JobsResponse
from mlb_statsapi.models.leagues import League, LeaguesResponse
from mlb_statsapi.models.livefeed import LiveFeedResponse
from mlb_statsapi.models.meta import MetaItem
from mlb_statsapi.models.people import PeopleResponse, Person
from mlb_statsapi.models.schedule import (
    ScheduleDate,
    ScheduleGame,
    ScheduleResponse,
)
from mlb_statsapi.models.seasons import Season, SeasonsResponse
from mlb_statsapi.models.sports import Sport, SportsResponse
from mlb_statsapi.models.standings import (
    StandingsRecord,
    StandingsResponse,
    TeamStanding,
)
from mlb_statsapi.models.stats import (
    LeaderCategory,
    LeaderEntry,
    StatsResponse,
)
from mlb_statsapi.models.teams import Team, TeamsResponse
from mlb_statsapi.models.transactions import Transaction, TransactionsResponse
from mlb_statsapi.models.venues import Venue, VenuesResponse

__all__ = [
    # Base
    "ApiLink",
    "BaseResponse",
    "CodeDescription",
    "GamePk",
    "GameStatus",
    "IdNameLink",
    "MlbBaseModel",
    "PersonId",
    "PersonRef",
    "PositionRef",
    "TeamId",
    "WinLossRecord",
    # Enums
    "AbstractGameState",
    "CodedGameState",
    "DayNight",
    "DetailedGameState",
    "DoubleHeaderCode",
    "EventType",
    "FieldingCredit",
    "GameType",
    "HalfInning",
    "HandCode",
    "HitTrajectory",
    "PitchCode",
    "PitchType",
    "PositionAbbreviation",
    "PositionType",
    "RosterType",
    "ScheduleEventType",
    "Sky",
    "StatGroup",
    "StatType",
    "StandingsType",
    "StreakType",
    "TiebreakerCode",
    "TransactionType",
    "WindDirection",
    # Domain models
    "AttendanceRecord",
    "AttendanceResponse",
    "Award",
    "AwardsResponse",
    "BoxscoreResponse",
    "Division",
    "DivisionsResponse",
    "Draft",
    "DraftPick",
    "DraftResponse",
    "DraftRound",
    "JobEntry",
    "JobsResponse",
    "LeaderCategory",
    "LeaderEntry",
    "League",
    "LeaguesResponse",
    "LinescoreResponse",
    "LiveFeedResponse",
    "MetaItem",
    "PeopleResponse",
    "Person",
    "ScheduleDate",
    "ScheduleGame",
    "ScheduleResponse",
    "Season",
    "SeasonsResponse",
    "Sport",
    "SportsResponse",
    "StandingsRecord",
    "StandingsResponse",
    "StatsResponse",
    "Team",
    "TeamStanding",
    "TeamsResponse",
    "Transaction",
    "TransactionsResponse",
    "Venue",
    "VenuesResponse",
]
