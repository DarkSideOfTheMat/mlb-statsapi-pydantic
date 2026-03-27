"""Game models — boxscore, linescore, live feed."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


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


class BoxscorePersonRef(MlbBaseModel):
    id: int
    full_name: str | None = None
    link: str | None = None


class BoxscorePosition(MlbBaseModel):
    code: str
    name: str | None = None
    type: str | None = None
    abbreviation: str | None = None


class BoxscorePlayer(MlbBaseModel):
    person: BoxscorePersonRef
    jersey_number: str | None = None
    position: BoxscorePosition | None = None
    parent_team_id: int | None = None
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
    batters: list[int] = []
    pitchers: list[int] = []
    bench: list[int] = []
    bullpen: list[int] = []
    batting_order: list[int] = []
    info: list[MlbBaseModel] = []
    note: list[MlbBaseModel] = []


class BoxscoreTeams(MlbBaseModel):
    away: BoxscoreTeam
    home: BoxscoreTeam


class BoxscoreOfficial(MlbBaseModel):
    official: BoxscorePersonRef | None = None
    official_type: str | None = None


class BoxscoreResponse(BaseResponse):
    teams: BoxscoreTeams
    officials: list[BoxscoreOfficial] = []
    info: list[MlbBaseModel] = []
    pitching_notes: list[str] = []


# --- Live Feed ---


class LiveGameData(MlbBaseModel):
    """Top-level gameData from live feed."""

    game: MlbBaseModel | None = None
    datetime: MlbBaseModel | None = None
    status: MlbBaseModel | None = None
    teams: MlbBaseModel | None = None
    venue: MlbBaseModel | None = None
    weather: MlbBaseModel | None = None
    game_info: MlbBaseModel | None = None
    probable_pitchers: MlbBaseModel | None = None


class LivePlays(MlbBaseModel):
    """Plays data from live feed."""

    all_plays: list[MlbBaseModel] = []
    current_play: MlbBaseModel | None = None
    scoring_plays: list[int] = []


class LiveData(MlbBaseModel):
    """Top-level liveData from live feed."""

    plays: LivePlays | None = None
    linescore: MlbBaseModel | None = None
    boxscore: MlbBaseModel | None = None
    decisions: MlbBaseModel | None = None
    leaders: MlbBaseModel | None = None


class LiveFeedResponse(BaseResponse):
    game_pk: int
    link: str | None = None
    meta_data: MlbBaseModel | None = None
    game_data: LiveGameData
    live_data: LiveData
