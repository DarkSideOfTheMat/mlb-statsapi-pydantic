"""Standings models.

Endpoint: ``/api/v1/standings``

Standings are organized by division within a league. Each team record
includes wins, losses, various rank types, games back, and elimination
numbers.
"""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    BaseResponse,
    DivisionId,
    LeagueId,
    MlbBaseModel,
    Ref,
    SportId,
    WinLossRecord,
)
from mlb_statsapi.models.divisions import Division
from mlb_statsapi.models.enums import StandingsType, StreakType
from mlb_statsapi.models.leagues import League
from mlb_statsapi.models.sports import Sport
from mlb_statsapi.models.teams import Team


class Streak(MlbBaseModel):
    """Current win or loss streak."""

    streak_code: str | None = None
    streak_type: StreakType | str | None = None
    streak_number: int | None = None


class TeamStanding(MlbBaseModel):
    """A team's standings record within a division.

    Games-back values are strings because the API uses ``"-"`` for the
    division leader. Use ``games_back_float`` to get a numeric value.
    """

    team: Team
    season: int | None = None
    streak: Streak | None = None
    clinch_indicator: str | None = None
    division_rank: str | None = None
    conference_rank: str | None = None
    league_rank: str | None = None
    spring_league_rank: str | None = None
    sport_rank: str | None = None
    wild_card_rank: str | None = None
    games_played: int | None = None
    games_back: str | None = None
    wild_card_games_back: str | None = None
    league_games_back: str | None = None
    spring_league_games_back: str | None = None
    sport_games_back: str | None = None
    division_games_back: str | None = None
    conference_games_back: str | None = None
    league_record: WinLossRecord | None = None
    last_updated: datetime.datetime | None = None
    wins: int | None = None
    losses: int | None = None
    winning_percentage: str | None = None
    runs_scored: int | None = None
    runs_allowed: int | None = None
    run_differential: int | None = None
    division_champ: bool | None = None
    division_leader: bool | None = None
    has_wildcard: bool | None = None
    clinched: bool | None = None
    elimination_number: str | None = None
    elimination_number_sport: str | None = None
    elimination_number_league: str | None = None
    elimination_number_division: str | None = None
    elimination_number_conference: str | None = None
    elimination_number_wildcard: str | None = None
    magic_number: str | None = None
    wild_card_elimination_number: str | None = None
    is_wild_card_team: bool | None = None
    points: int | None = None
    place: int | None = None
    wildcard_place: int | None = None

    @property
    def games_back_float(self) -> float | None:
        """Parse games_back string (``"-"`` or ``"5.0"``) into float."""
        if self.games_back is None:
            return None
        if self.games_back == "-":
            return 0.0
        try:
            return float(self.games_back)
        except ValueError:
            return None


class StandingsRecord(MlbBaseModel):
    """Standings grouped by division/league/type."""

    standings_type: StandingsType | str
    league: League | Ref[LeagueId]
    division: Division | Ref[DivisionId]
    sport: Sport | Ref[SportId] | None = None
    last_updated: datetime.datetime | None = None
    team_records: list[TeamStanding] = []


class StandingsResponse(BaseResponse):
    """Response from ``/api/v1/standings``."""

    records: list[StandingsRecord] = []
