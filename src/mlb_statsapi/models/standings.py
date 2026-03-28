"""Standings models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import (
    BaseResponse,
    IdNameLink,
    MlbBaseModel,
    WinLossRecord,
)
from mlb_statsapi.models.enums import StandingsType, StreakType


class Streak(MlbBaseModel):
    streak_code: str | None = None
    streak_type: StreakType | str | None = None
    streak_number: int | None = None



class TeamStanding(MlbBaseModel):
    team: IdNameLink
    season: int
    streak: Streak | None = None
    clinch_indicator: str | None = None
    division_rank: str | None = None
    league_rank: str | None = None
    sport_rank: str | None = None
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
    clinched: bool | None = None
    elimination_number: str | None = None
    magic_number: str | None = None
    wild_card_elimination_number: str | None = None

    @property
    def games_back_float(self) -> float | None:
        """Parse games_back string ('-' or '5.0') into float."""
        if self.games_back is None:
            return None
        if self.games_back == "-":
            return 0.0
        try:
            return float(self.games_back)
        except ValueError:
            return None


class StandingsRecord(MlbBaseModel):
    standings_type: StandingsType | str
    league: IdNameLink
    division: IdNameLink
    sport: IdNameLink | None = None
    last_updated: datetime.datetime | None = None
    team_records: list[TeamStanding] = []


class StandingsResponse(BaseResponse):
    records: list[StandingsRecord] = []
