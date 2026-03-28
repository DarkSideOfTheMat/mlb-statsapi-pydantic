"""Game models — boxscore, linescore, live feed."""

from __future__ import annotations

from mlb_statsapi.models._base import (
    BaseResponse,
    IdNameLink,
    MlbBaseModel,
    PersonId,
    PersonRef,
    PositionRef,
    TeamId,
)

# --- Linescore ---


class InningTeamLine(MlbBaseModel):
    runs: int | None = None
    hits: int | None = None
    errors: int | None = None
    left_on_base: int | None = None


class LinescoreInning(MlbBaseModel):
    num: int
    ordinal_num: str | None = None
    home: InningTeamLine
    away: InningTeamLine


class LinescoreTeamTotal(MlbBaseModel):
    runs: int | None = None
    hits: int | None = None
    errors: int | None = None
    left_on_base: int | None = None
    is_winner: bool | None = None


class LinescoreTeams(MlbBaseModel):
    home: LinescoreTeamTotal
    away: LinescoreTeamTotal


class LinescoreResponse(BaseResponse):
    current_inning: int | None = None
    current_inning_ordinal: str | None = None
    inning_state: str | None = None
    inning_half: str | None = None
    is_top_inning: bool | None = None
    scheduled_innings: int | None = None
    innings: list[LinescoreInning] = []
    teams: LinescoreTeams | None = None


# --- Boxscore ---


# Backwards-compatible aliases
BoxscorePersonRef = PersonRef
BoxscorePosition = PositionRef


class BoxscorePlayer(MlbBaseModel):
    person: PersonRef
    jersey_number: str | None = None
    position: PositionRef | None = None
    parent_team_id: TeamId | None = None
    stats: MlbBaseModel | None = None
    season_stats: MlbBaseModel | None = None
    game_status: MlbBaseModel | None = None
    status: MlbBaseModel | None = None


class BoxscoreTeamStats(MlbBaseModel):
    batting: dict[str, int | str | float] | None = None
    pitching: dict[str, int | str | float] | None = None
    fielding: dict[str, int | str | float] | None = None


class BoxscoreTeam(MlbBaseModel):
    team: IdNameLink
    team_stats: BoxscoreTeamStats | None = None
    players: dict[str, BoxscorePlayer] = {}
    batters: list[PersonId] = []
    pitchers: list[PersonId] = []
    bench: list[PersonId] = []
    bullpen: list[PersonId] = []
    batting_order: list[PersonId] = []
    info: list[MlbBaseModel] = []
    note: list[MlbBaseModel] = []


class BoxscoreTeams(MlbBaseModel):
    away: BoxscoreTeam
    home: BoxscoreTeam


class BoxscoreOfficial(MlbBaseModel):
    official: PersonRef | None = None
    official_type: str | None = None


class BoxscoreResponse(BaseResponse):
    teams: BoxscoreTeams
    officials: list[BoxscoreOfficial] = []
    info: list[MlbBaseModel] = []
    pitching_notes: list[str] = []
