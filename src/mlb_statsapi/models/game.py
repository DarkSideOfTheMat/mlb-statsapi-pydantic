"""Game models — boxscore, linescore, live feed."""

from __future__ import annotations

from mlb_statsapi.models._base import (
    BaseResponse,
    CodeDescription,
    IdNameLink,
    MlbBaseModel,
    PersonId,
    PersonRef,
    PositionRef,
    TeamId,
)
from mlb_statsapi.models.enums import HalfInning

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
    inning_half: HalfInning | str | None = None
    is_top_inning: bool | None = None
    scheduled_innings: int | None = None
    innings: list[LinescoreInning] = []
    teams: LinescoreTeams | None = None


# --- Boxscore ---


# Backwards-compatible aliases
BoxscorePersonRef = PersonRef
BoxscorePosition = PositionRef


class BoxscoreInfoField(MlbBaseModel):
    """A single label/value field within a boxscore info section."""

    label: str | None = None
    value: str | None = None


class BoxscoreInfo(MlbBaseModel):
    """A titled section of boxscore info (e.g. BATTING, FIELDING)."""

    title: str | None = None
    field_list: list[BoxscoreInfoField] = []


class PlayerGameStats(MlbBaseModel):
    """Batting/pitching/fielding stats for a player in a game context."""

    batting: dict[str, object] = {}
    pitching: dict[str, object] = {}
    fielding: dict[str, object] = {}


class PlayerGameStatus(MlbBaseModel):
    """Player in-game status flags."""

    is_current_batter: bool | None = None
    is_current_pitcher: bool | None = None
    is_on_bench: bool | None = None
    is_substitute: bool | None = None


class BoxscorePlayer(MlbBaseModel):
    person: PersonRef
    jersey_number: str | None = None
    position: PositionRef | None = None
    parent_team_id: TeamId | None = None
    stats: PlayerGameStats | None = None
    season_stats: PlayerGameStats | None = None
    game_status: PlayerGameStatus | None = None
    status: CodeDescription | None = None


class BoxscoreTeamStats(MlbBaseModel):
    batting: dict[str, object] | None = None
    pitching: dict[str, object] | None = None
    fielding: dict[str, object] | None = None


class BoxscoreTeam(MlbBaseModel):
    team: IdNameLink
    team_stats: BoxscoreTeamStats | None = None
    players: dict[str, BoxscorePlayer] = {}
    batters: list[PersonId] = []
    pitchers: list[PersonId] = []
    bench: list[PersonId] = []
    bullpen: list[PersonId] = []
    batting_order: list[PersonId] = []
    info: list[BoxscoreInfo] = []
    note: list[BoxscoreInfoField] = []

    def _resolve_ids(
        self, ids: list[PersonId],
    ) -> list[BoxscorePlayer]:
        """Resolve a list of player IDs to BoxscorePlayer objects."""
        return [
            self.players[key]
            for pid in ids
            if (key := f"ID{pid}") in self.players
        ]

    @property
    def batter_players(self) -> list[BoxscorePlayer]:
        """Resolve batter IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.batters)

    @property
    def pitcher_players(self) -> list[BoxscorePlayer]:
        """Resolve pitcher IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.pitchers)

    @property
    def bench_players(self) -> list[BoxscorePlayer]:
        """Resolve bench IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.bench)

    @property
    def bullpen_players(self) -> list[BoxscorePlayer]:
        """Resolve bullpen IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.bullpen)

    @property
    def batting_order_players(self) -> list[BoxscorePlayer]:
        """Resolve batting_order IDs to BoxscorePlayer objects."""
        return self._resolve_ids(self.batting_order)


class BoxscoreTeams(MlbBaseModel):
    away: BoxscoreTeam
    home: BoxscoreTeam


class BoxscoreOfficial(MlbBaseModel):
    official: PersonRef | None = None
    official_type: str | None = None


class BoxscoreResponse(BaseResponse):
    teams: BoxscoreTeams
    officials: list[BoxscoreOfficial] = []
    info: list[BoxscoreInfoField] = []
    pitching_notes: list[str] = []
