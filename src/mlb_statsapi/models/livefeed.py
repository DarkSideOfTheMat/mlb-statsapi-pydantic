"""Live feed and play-by-play models.

The live feed (``/api/v1.1/game/{gamePk}/feed/live``) is the richest
single endpoint in the MLB Stats API, containing the full game state
including every play, pitch, and runner movement.
"""

from __future__ import annotations

from mlb_statsapi.models._base import (
    BaseResponse,
    CodeDescription,
    IdNameLink,
    MlbBaseModel,
)

# ---------------------------------------------------------------------------
# Shared reference types used across plays
# ---------------------------------------------------------------------------


class PersonRef(MlbBaseModel):
    """Lightweight person reference used throughout play data."""

    id: int
    full_name: str | None = None
    link: str | None = None


class PositionRef(MlbBaseModel):
    """Position reference (not IdNameLink — uses code, not id)."""

    code: str
    name: str | None = None
    type: str | None = None
    abbreviation: str | None = None


# ---------------------------------------------------------------------------
# Pitch data — the core of play events
# ---------------------------------------------------------------------------


class PitchCoordinates(MlbBaseModel):
    """Pitch tracking coordinates (PITCHf/x and Statcast)."""

    a_x: float | None = None
    a_y: float | None = None
    a_z: float | None = None
    pfx_x: float | None = None
    pfx_z: float | None = None
    p_x: float | None = None
    p_z: float | None = None
    v_x0: float | None = None
    v_y0: float | None = None
    v_z0: float | None = None
    x: float | None = None
    y: float | None = None
    x0: float | None = None
    y0: float | None = None
    z0: float | None = None


class PitchBreaks(MlbBaseModel):
    """Pitch break data."""

    break_angle: float | None = None
    break_length: float | None = None
    break_y: float | None = None
    break_vertical: float | None = None
    break_vertical_induced: float | None = None
    break_horizontal: float | None = None
    spin_rate: int | None = None
    spin_direction: int | None = None


class PitchType(MlbBaseModel):
    """Pitch classification (e.g. FF = Four-Seam Fastball)."""

    code: str
    description: str | None = None


class PitchData(MlbBaseModel):
    """Statcast pitch tracking data."""

    start_speed: float | None = None
    end_speed: float | None = None
    strike_zone_top: float | None = None
    strike_zone_bottom: float | None = None
    coordinates: PitchCoordinates | None = None
    breaks: PitchBreaks | None = None
    zone: int | None = None
    type_confidence: float | None = None
    plate_time: float | None = None
    extension: float | None = None


# ---------------------------------------------------------------------------
# Play events — individual pitches and actions within an at-bat
# ---------------------------------------------------------------------------


class PlayEventCall(MlbBaseModel):
    """Umpire call on a pitch (B, S, X, etc.)."""

    code: str
    description: str | None = None


class PlayEventDetails(MlbBaseModel):
    """Details for a single play event (pitch or action)."""

    call: PlayEventCall | None = None
    description: str | None = None
    code: str | None = None
    ball_color: str | None = None
    trail_color: str | None = None
    is_in_play: bool | None = None
    is_strike: bool | None = None
    is_ball: bool | None = None
    type: PitchType | None = None
    is_out: bool | None = None
    has_review: bool | None = None
    # Action-specific fields
    event: str | None = None
    event_type: str | None = None
    away_score: int | None = None
    home_score: int | None = None
    is_scoring_play: bool | None = None


class Count(MlbBaseModel):
    """Ball-strike-out count."""

    balls: int = 0
    strikes: int = 0
    outs: int = 0


class PlayEvent(MlbBaseModel):
    """A single event within a play — either a pitch or an action.

    Pitch events have ``is_pitch=True``, ``pitch_data``, and ``pitch_number``.
    Action events have ``type="action"`` and action-specific details.
    """

    details: PlayEventDetails | None = None
    count: Count | None = None
    pitch_data: PitchData | None = None
    index: int | None = None
    play_id: str | None = None
    pitch_number: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    is_pitch: bool | None = None
    type: str | None = None
    player: PersonRef | None = None

    @property
    def is_action(self) -> bool:
        return self.type == "action"


# ---------------------------------------------------------------------------
# Runner movement
# ---------------------------------------------------------------------------


class RunnerMovement(MlbBaseModel):
    """Base-to-base runner movement."""

    origin_base: str | None = None
    start: str | None = None
    end: str | None = None
    out_base: str | None = None
    is_out: bool | None = None
    out_number: int | None = None


class RunnerDetails(MlbBaseModel):
    """Details about a runner's action during a play."""

    event: str | None = None
    event_type: str | None = None
    movement_reason: str | None = None
    runner: PersonRef | None = None
    responsible_pitcher: PersonRef | None = None
    is_scoring_event: bool | None = None
    rbi: bool | None = None
    earned: bool | None = None
    team_unearned: bool | None = None
    play_index: int | None = None


class RunnerCredit(MlbBaseModel):
    """Fielding credit for a runner event (putout, assist, etc.)."""

    player: PersonRef | None = None
    position: PositionRef | None = None
    credit: str | None = None


class Runner(MlbBaseModel):
    """A runner's movement and outcome during a play."""

    movement: RunnerMovement | None = None
    details: RunnerDetails | None = None
    credits: list[RunnerCredit] = []


# ---------------------------------------------------------------------------
# Matchup
# ---------------------------------------------------------------------------


class MatchupSplits(MlbBaseModel):
    """Batter/pitcher split context."""

    batter: str | None = None
    pitcher: str | None = None
    men_on_base: str | None = None


class Matchup(MlbBaseModel):
    """Batter vs. pitcher matchup for an at-bat."""

    batter: PersonRef
    bat_side: CodeDescription | None = None
    pitcher: PersonRef
    pitch_hand: CodeDescription | None = None
    batter_hot_cold_zones: list[MlbBaseModel] = []
    pitcher_hot_cold_zones: list[MlbBaseModel] = []
    splits: MatchupSplits | None = None


# ---------------------------------------------------------------------------
# Play (at-bat) — the central model
# ---------------------------------------------------------------------------


class PlayResult(MlbBaseModel):
    """Outcome of an at-bat."""

    type: str | None = None
    event: str | None = None
    event_type: str | None = None
    description: str | None = None
    rbi: int | None = None
    away_score: int | None = None
    home_score: int | None = None
    is_out: bool | None = None


class PlayAbout(MlbBaseModel):
    """Metadata about when/where a play occurred."""

    at_bat_index: int | None = None
    half_inning: str | None = None
    is_top_inning: bool | None = None
    inning: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    is_complete: bool | None = None
    is_scoring_play: bool | None = None
    has_review: bool | None = None
    has_out: bool | None = None
    captivating_index: int | None = None


class Play(MlbBaseModel):
    """A complete at-bat with all pitches, runners, and outcome.

    This is the central play-by-play model. Each play contains:
    - ``result``: final outcome (event type, description, score)
    - ``about``: inning, timing, and flags
    - ``count``: final ball/strike/out count
    - ``matchup``: batter vs pitcher with handedness and splits
    - ``play_events``: ordered list of pitches and actions
    - ``runners``: base movement and fielding credits
    """

    result: PlayResult | None = None
    about: PlayAbout | None = None
    count: Count | None = None
    matchup: Matchup | None = None
    pitch_index: list[int] = []
    action_index: list[int] = []
    runner_index: list[int] = []
    runners: list[Runner] = []
    play_events: list[PlayEvent] = []
    play_end_time: str | None = None
    at_bat_index: int | None = None


# ---------------------------------------------------------------------------
# Plays container and plays-by-inning
# ---------------------------------------------------------------------------


class InningPlays(MlbBaseModel):
    """Play indices grouped by inning."""

    start_index: int | None = None
    end_index: int | None = None
    top: list[int] = []
    bottom: list[int] = []
    hits: MlbBaseModel | None = None


class Plays(MlbBaseModel):
    """All play data for the game."""

    all_plays: list[Play] = []
    current_play: Play | None = None
    scoring_plays: list[int] = []
    plays_by_inning: list[InningPlays] = []


# ---------------------------------------------------------------------------
# Decisions (winning/losing pitcher, save)
# ---------------------------------------------------------------------------


class Decisions(MlbBaseModel):
    winner: PersonRef | None = None
    loser: PersonRef | None = None
    save: PersonRef | None = None


# ---------------------------------------------------------------------------
# Game data (top-level gameData in live feed)
# ---------------------------------------------------------------------------


class GameDataStatus(MlbBaseModel):
    abstract_game_state: str | None = None
    coded_game_state: str | None = None
    detailed_state: str | None = None
    status_code: str | None = None
    start_time_tbd: bool | None = None
    abstract_game_code: str | None = None


class GameDataTeamRecord(MlbBaseModel):
    wins: int | None = None
    losses: int | None = None
    pct: str | None = None


class GameDataTeam(MlbBaseModel):
    id: int
    name: str | None = None
    link: str | None = None
    record: GameDataTeamRecord | None = None


class GameDataTeams(MlbBaseModel):
    away: GameDataTeam | None = None
    home: GameDataTeam | None = None


class Weather(MlbBaseModel):
    condition: str | None = None
    temp: str | None = None
    wind: str | None = None


class ProbablePitchers(MlbBaseModel):
    away: PersonRef | None = None
    home: PersonRef | None = None


class GameData(MlbBaseModel):
    """Top-level gameData from live feed."""

    game: MlbBaseModel | None = None
    datetime: MlbBaseModel | None = None
    status: GameDataStatus | None = None
    teams: GameDataTeams | None = None
    venue: IdNameLink | None = None
    official_venue: IdNameLink | None = None
    weather: Weather | None = None
    game_info: MlbBaseModel | None = None
    review: MlbBaseModel | None = None
    flags: MlbBaseModel | None = None
    probable_pitchers: ProbablePitchers | None = None


# ---------------------------------------------------------------------------
# Live data and response
# ---------------------------------------------------------------------------


class LiveData(MlbBaseModel):
    """Top-level liveData from live feed."""

    plays: Plays | None = None
    linescore: MlbBaseModel | None = None
    boxscore: MlbBaseModel | None = None
    decisions: Decisions | None = None
    leaders: MlbBaseModel | None = None


class LiveFeedResponse(BaseResponse):
    """Full live game feed response.

    This is the largest and most detailed response in the API, containing
    the complete game state: all plays with pitch-level data, linescore,
    boxscore, decisions, and game metadata.
    """

    game_pk: int
    link: str | None = None
    meta_data: MlbBaseModel | None = None
    game_data: GameData
    live_data: LiveData
