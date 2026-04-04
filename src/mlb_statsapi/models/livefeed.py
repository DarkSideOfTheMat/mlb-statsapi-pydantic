"""Live feed and play-by-play models.

Endpoints:

- ``/api/v1.1/game/{gamePk}/feed/live`` → :class:`LiveFeedResponse`
- ``/api/v1/game/{gamePk}/playByPlay`` → :class:`PlayByPlayResponse`

The live feed is the richest single endpoint in the MLB Stats API,
containing the full game state including every play, pitch, and runner
movement. The response is structured as two top-level sections:

- ``gameData`` — static game metadata (teams, players, venue, weather)
- ``liveData`` — dynamic game state (plays, linescore, boxscore, decisions)

The play-by-play endpoint returns a subset: just the plays data
(all plays, scoring plays, plays by inning) without game metadata.

The GUMBO (Game Used MlB Objects) feed provides granular data including
Statcast pitch tracking (velocity, spin, movement, coordinates) and
hit data (exit velocity, launch angle, distance).
"""

from __future__ import annotations

import datetime

from pydantic import Field

from mlb_statsapi.models._base import (
    ApiLink,
    BaseResponse,
    CodeDescription,
    GamePk,
    GameStatus,
    MlbBaseModel,
    PersonRef,
    PositionRef,
    Ref,
    TeamId,
    VenueId,
    WinLossRecord,
)
from mlb_statsapi.models.enums import (
    DayNight,
    DoubleHeaderCode,
    EventType,
    FieldingCredit,
    GameType,
    HalfInning,
    HitTrajectory,
    PitchCode,
    Sky,
    TiebreakerCode,
)
from mlb_statsapi.models.enums import (
    PitchType as PitchTypeEnum,
)
from mlb_statsapi.models.game import Boxscore, Linescore
from mlb_statsapi.models.people import Person
from mlb_statsapi.models.venues import Venue

# ---------------------------------------------------------------------------
# Pitch data — the core of play events
# ---------------------------------------------------------------------------


class PitchCoordinates(MlbBaseModel):
    """Pitch tracking coordinates (PITCHf/x and Statcast).

    Contains acceleration, movement, velocity, and position data
    for a pitch from release to the plate.
    """

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
    """Pitch break and spin data.

    ``spin_rate`` is in RPM, ``spin_direction`` is in degrees.
    Break measurements describe horizontal and vertical movement.
    """

    break_angle: float | None = None
    break_length: float | None = None
    break_y: float | None = None
    break_vertical: float | None = None
    break_vertical_induced: float | None = None
    break_horizontal: float | None = None
    spin_rate: int | None = None
    spin_direction: int | None = None


class PitchTypeInfo(MlbBaseModel):
    """Pitch classification (e.g. FF = Four-Seam Fastball)."""

    code: PitchTypeEnum | str
    description: str | None = None


class HitData(MlbBaseModel):
    """Statcast hit tracking data.

    Contains exit velocity (``launch_speed``), launch angle, total
    distance, trajectory classification, and barrel designation.
    """

    launch_speed: float | None = None
    launch_angle: float | None = None
    total_distance: float | None = None
    trajectory: HitTrajectory | str | None = None
    hardness: str | None = None
    location: str | None = None
    coordinates: MlbBaseModel | None = None
    is_barrel: bool | None = None
    hit_probability: float | None = None
    bat_speed: float | None = None
    is_sword_swing: bool | None = None


class PitchData(MlbBaseModel):
    """Statcast pitch tracking data.

    ``start_speed`` and ``end_speed`` are in MPH. ``zone`` is the
    strike zone region (1-14, see plate zone diagram). ``plate_time``
    is seconds from release to plate. ``extension`` is pitcher's
    release extension in feet.
    """

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

    code: PitchCode | str
    description: str | None = None


class PlayEventDetails(MlbBaseModel):
    """Details for a single play event (pitch or action).

    Pitch events include the call, pitch type, and in-play flags.
    Action events include the event type and scoring information.
    """

    call: PlayEventCall | None = None
    description: str | None = None
    code: str | None = None
    ball_color: str | None = None
    trail_color: str | None = None
    is_in_play: bool | None = None
    is_strike: bool | None = None
    is_ball: bool | None = None
    type: PitchTypeInfo | None = None
    is_out: bool | None = None
    has_review: bool | None = None
    # Action-specific fields
    event: str | None = None
    event_type: EventType | str | None = None
    away_score: int | None = None
    home_score: int | None = None
    is_scoring_play: bool | None = None


class Count(MlbBaseModel):
    """Ball-strike-out count at a point in time."""

    balls: int = 0
    strikes: int = 0
    outs: int = 0


class PlayEvent(MlbBaseModel):
    """A single event within a play — either a pitch or an action.

    Pitch events have ``is_pitch=True``, ``pitch_data``, and ``pitch_number``.
    Action events have ``type="action"`` and action-specific details.
    Hit data is present when the ball is put in play.
    """

    details: PlayEventDetails | None = None
    count: Count | None = None
    pitch_data: PitchData | None = None
    hit_data: HitData | None = None
    index: int | None = None
    play_id: str | None = None
    pitch_number: int | None = None
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    is_pitch: bool | None = None
    type: str | None = None
    player: PersonRef | None = None
    position: PositionRef | None = None
    batting_order: str | None = None
    is_substitution: bool | None = None
    is_base_running_play: bool | None = None

    @property
    def is_action(self) -> bool:
        """Whether this event is an action (substitution, etc.) rather than a pitch."""
        return self.type == "action"


# ---------------------------------------------------------------------------
# Runner movement
# ---------------------------------------------------------------------------


class RunnerMovement(MlbBaseModel):
    """Base-to-base runner movement within a play."""

    origin_base: str | None = None
    start: str | None = None
    end: str | None = None
    out_base: str | None = None
    is_out: bool | None = None
    out_number: int | None = None


class RunnerDetails(MlbBaseModel):
    """Details about a runner's action during a play."""

    event: str | None = None
    event_type: EventType | str | None = None
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
    credit: FieldingCredit | str | None = None


class Runner(MlbBaseModel):
    """A runner's movement and outcome during a play.

    Combines the physical movement (base to base), the event details,
    and any fielding credits earned.
    """

    movement: RunnerMovement | None = None
    details: RunnerDetails | None = None
    credits: list[RunnerCredit] = []


# ---------------------------------------------------------------------------
# Matchup
# ---------------------------------------------------------------------------


class MatchupSplits(MlbBaseModel):
    """Batter/pitcher split context (e.g. vs LHP, runners on base)."""

    batter: str | None = None
    pitcher: str | None = None
    men_on_base: str | None = None


class HotColdZone(MlbBaseModel):
    """Strike zone heat map zone for a batter or pitcher.

    Used to display hot/cold zone overlays on the strike zone.
    """

    zone: str | None = None
    color: str | None = None
    temp: str | None = None
    value: str | None = None


class Matchup(MlbBaseModel):
    """Batter vs. pitcher matchup for an at-bat.

    Includes handedness, hot/cold zones, and split context.
    """

    batter: PersonRef
    bat_side: CodeDescription | None = None
    pitcher: PersonRef
    pitch_hand: CodeDescription | None = None
    batter_hot_cold_zones: list[HotColdZone] = []
    pitcher_hot_cold_zones: list[HotColdZone] = []
    splits: MatchupSplits | None = None


# ---------------------------------------------------------------------------
# Play (at-bat) — the central model
# ---------------------------------------------------------------------------


class PlayResult(MlbBaseModel):
    """Outcome of an at-bat.

    Contains the event type, description, RBI count, and resulting score.
    """

    type: str | None = None
    event: str | None = None
    event_type: EventType | str | None = None
    description: str | None = None
    rbi: int | None = None
    away_score: int | None = None
    home_score: int | None = None
    is_out: bool | None = None


class PlayAbout(MlbBaseModel):
    """Metadata about when/where a play occurred.

    Includes the inning, half, timing, and various flags.
    ``captivating_index`` is an API-computed excitement score.
    """

    at_bat_index: int | None = None
    half_inning: HalfInning | str | None = None
    is_top_inning: bool | None = None
    inning: int | None = None
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
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
    play_end_time: datetime.datetime | None = None
    at_bat_index: int | None = None
    is_double_play: bool | None = None
    is_triple_play: bool | None = None
    is_grounded_into_double_play: bool | None = None

    # Win probability fields — only present in /game/{gamePk}/winProbability responses
    home_team_win_probability: float | None = None
    away_team_win_probability: float | None = None
    home_team_win_probability_added: float | None = None
    context_metrics: MlbBaseModel | None = None
    credits: list[MlbBaseModel] = []
    flags: list[MlbBaseModel] = []

    @property
    def pitches(self) -> list[PlayEvent]:
        """Resolve pitch_index to PlayEvent objects."""
        n = len(self.play_events)
        return [self.play_events[i] for i in self.pitch_index if i < n]

    @property
    def actions(self) -> list[PlayEvent]:
        """Resolve action_index to PlayEvent objects."""
        n = len(self.play_events)
        return [self.play_events[i] for i in self.action_index if i < n]

    @property
    def indexed_runners(self) -> list[Runner]:
        """Resolve runner_index to Runner objects."""
        return [self.runners[i] for i in self.runner_index if i < len(self.runners)]


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

    @property
    def scoring_play_objects(self) -> list[Play]:
        """Resolve scoring_plays indices to Play objects."""
        n = len(self.all_plays)
        return [self.all_plays[i] for i in self.scoring_plays if i < n]


# ---------------------------------------------------------------------------
# Decisions (winning/losing pitcher, save)
# ---------------------------------------------------------------------------


class Decisions(MlbBaseModel):
    """Game decisions — winning pitcher, losing pitcher, and save."""

    winner: PersonRef | None = None
    loser: PersonRef | None = None
    save: PersonRef | None = None


# ---------------------------------------------------------------------------
# Game data (top-level gameData in live feed)
# ---------------------------------------------------------------------------


class GameInfo(MlbBaseModel):
    """Game identification from ``gameData.game``."""

    pk: GamePk | None = None
    type: GameType | str | None = None
    double_header: DoubleHeaderCode | str | None = None
    id: str | None = None
    gameday_type: str | None = None
    tiebreaker: TiebreakerCode | str | None = None
    game_number: int | None = None
    calendar_event_id: str | None = None
    season: str | None = None
    season_display: str | None = None


class GameDateTime(MlbBaseModel):
    """Date and time info from ``gameData.datetime``."""

    date_time: datetime.datetime | None = None
    original_date: str | None = None
    official_date: str | None = None
    day_night: DayNight | str | None = None
    time: str | None = None
    ampm: str | None = None


class GameInfoDetails(MlbBaseModel):
    """Game logistics from ``gameData.gameInfo``.

    Contains attendance, first pitch time, and game duration.
    """

    attendance: int | None = None
    first_pitch: datetime.datetime | None = None
    game_duration_minutes: int | None = None


class ReviewTeam(MlbBaseModel):
    """Challenge review counts for one team."""

    used: int | None = None
    remaining: int | None = None


class ReviewInfo(MlbBaseModel):
    """Manager challenge review info."""

    has_challenges: bool | None = None
    away: ReviewTeam | None = None
    home: ReviewTeam | None = None


class GameFlags(MlbBaseModel):
    """No-hitter and perfect game flags.

    Tracked per-team and combined for the overall game.
    """

    no_hitter: bool | None = None
    perfect_game: bool | None = None
    away_team_no_hitter: bool | None = None
    away_team_perfect_game: bool | None = None
    home_team_no_hitter: bool | None = None
    home_team_perfect_game: bool | None = None


class GameDataTeam(MlbBaseModel):
    """Team info within ``gameData.teams``."""

    id: TeamId
    name: str | None = None
    link: ApiLink | None = None
    record: WinLossRecord | None = None


class GameDataTeams(MlbBaseModel):
    """Away and home teams in ``gameData.teams``."""

    away: GameDataTeam | None = None
    home: GameDataTeam | None = None


class Weather(MlbBaseModel):
    """Weather conditions at game time."""

    condition: Sky | str | None = None
    temp: str | None = None
    wind: str | None = None


class ProbablePitchers(MlbBaseModel):
    """Probable starting pitchers for the game."""

    away: PersonRef | None = None
    home: PersonRef | None = None


class GameData(MlbBaseModel):
    """Top-level ``gameData`` from live feed.

    Contains static game metadata: identification, date/time, status,
    teams, players, venue, weather, and review information.
    """

    game: GameInfo | None = None
    datetime: GameDateTime | None = None
    status: GameStatus | None = None
    teams: GameDataTeams | None = None
    venue: Venue | Ref[VenueId] | None = None
    official_venue: Venue | Ref[VenueId] | None = None
    weather: Weather | None = None
    game_info: GameInfoDetails | None = None
    review: ReviewInfo | None = None
    flags: GameFlags | None = None
    probable_pitchers: ProbablePitchers | None = None
    players: dict[str, Person] | None = None


# ---------------------------------------------------------------------------
# Live data and response
# ---------------------------------------------------------------------------


class LiveData(MlbBaseModel):
    """Top-level ``liveData`` from live feed.

    Contains the dynamic game state: play-by-play data, linescore,
    boxscore, decisions, and leaders.
    """

    plays: Plays | None = None
    linescore: Linescore | None = None
    boxscore: Boxscore | None = None
    decisions: Decisions | None = None
    leaders: MlbBaseModel | None = None


class LiveFeedResponse(BaseResponse):
    """Response from ``/api/v1.1/game/{gamePk}/feed/live``.

    This is the largest and most detailed response in the API, containing
    the complete game state: all plays with pitch-level Statcast data,
    linescore, boxscore, decisions, and game metadata.

    Available hydrations: ``credits``, ``alignment``, ``flags``,
    ``officials``, ``preState``.
    """

    game_pk: GamePk
    link: ApiLink | None = None
    meta_data: MlbBaseModel | None = None
    game_data: GameData
    live_data: LiveData


class PlayByPlayResponse(BaseResponse):
    """Response from ``/api/v1/game/{gamePk}/playByPlay``.

    Contains the same play data as ``liveData.plays`` in the live feed,
    but as a standalone response. The ``scoring_plays`` property returns
    resolved :class:`Play` objects; use ``scoring_play_indices`` for the
    raw integer indices from the API.
    """

    all_plays: list[Play] = []
    current_play: Play | None = None
    scoring_play_indices: list[int] = Field(default=[], alias="scoringPlays")
    plays_by_inning: list[InningPlays] = []

    @property
    def scoring_plays(self) -> list[Play]:
        """Resolve scoring play indices to Play objects."""
        n = len(self.all_plays)
        return [self.all_plays[i] for i in self.scoring_play_indices if i < n]
