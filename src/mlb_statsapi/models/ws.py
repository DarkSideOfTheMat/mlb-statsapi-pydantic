"""WebSocket push notification models.

The MLB Stats API pushes lightweight JSON notifications via a WebSocket
at ``wss://ws.statsapi.mlb.com/api/v1/game/push/subscribe/gameday/<gamePk>``.

These messages contain event classifications (``logicalEvents``,
``gameEvents``) and a ``timeStamp`` but **not** full game data. Clients
use these notifications to decide when to fire REST requests for the
full game state based on user-configured granularity.

.. note::
    This WebSocket endpoint is undocumented. The enum values below are
    based on observed traffic and may be incomplete. All enum-typed fields
    use the ``EnumType | str`` pattern so that unknown values are accepted.
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport of StrEnum for Python < 3.11."""


from mlb_statsapi.models._base import MlbBaseModel

# ---------------------------------------------------------------------------
# WebSocket event enums — known values, open-ended
# ---------------------------------------------------------------------------


class WsLogicalEvent(StrEnum):
    """Known ``logicalEvents`` values from the gameday WebSocket.

    These describe logical state changes in the game. The list is
    non-exhaustive — unknown values are accepted via ``| str``.
    """

    # Count
    COUNT_CHANGE = "countChange"
    COUNT_00 = "count00"
    COUNT_01 = "count01"
    COUNT_02 = "count02"
    COUNT_03 = "count03"
    COUNT_10 = "count10"
    COUNT_11 = "count11"
    COUNT_12 = "count12"
    COUNT_13 = "count13"
    COUNT_20 = "count20"
    COUNT_21 = "count21"
    COUNT_22 = "count22"
    COUNT_23 = "count23"
    COUNT_30 = "count30"
    COUNT_31 = "count31"
    COUNT_32 = "count32"
    COUNT_33 = "count33"
    COUNT_40 = "count40"
    COUNT_41 = "count41"
    COUNT_42 = "count42"

    # Batter
    NEW_BATTER = "newBatter"
    NEW_RIGHT_HANDED_HIT = "newRightHandedHit"
    NEW_LEFT_HANDED_HIT = "newLeftHandedHit"
    BATTER_SWITCHED_TO_LEFT_HANDED = "batterSwitchedToLeftHanded"
    BATTER_SWITCHED_TO_RIGHT_HANDED = "batterSwitchedToRightHanded"

    # Baserunners
    BASES_EMPTY = "basesEmpty"
    RUNNER_ON_FIRST = "runnerOnFirst"
    RUNNER_ON_SECOND = "runnerOnSecond"
    RUNNER_ON_THIRD = "runnerOnThird"
    RUNNERS_ON_FIRST_AND_SECOND = "runnersOnFirstAndSecond"
    RUNNERS_ON_FIRST_AND_THIRD = "runnersOnFirstAndThird"
    RUNNERS_ON_SECOND_AND_THIRD = "runnersOnSecondAndThird"
    RUNNERS_IN_SCORING_POSITION = "runnersInScoringPosition"
    BASES_LOADED = "basesLoaded"

    # Inning
    NEW_HALF_INNING = "newHalfInning"
    MID_INNING = "midInning"

    # Pitcher
    PITCHER_CHANGE = "pitcherChange"
    PITCHER_CHANGE_COMPLETE = "pitcherChangeComplete"

    # Defense
    DEFENSIVE_SUBSTITUTION = "defensiveSubstitution"


class WsGameEvent(StrEnum):
    """Known ``gameEvents`` values from the gameday WebSocket.

    These describe game-level events. The list is non-exhaustive —
    unknown values are accepted via ``| str``.

    .. note::
        Values use **snake_case** (e.g. ``called_strike``, not ``calledStrike``).
    """

    # Pitches
    BALL = "ball"
    CALLED_STRIKE = "called_strike"
    SWINGING_STRIKE = "swinging_strike"
    FOUL = "foul"
    FOUL_TIP = "foul_tip"
    FOUL_BUNT = "foul_bunt"
    BLOCKED_BALL = "blocked_ball"
    HIT_INTO_PLAY = "hit_into_play"
    HIT_INTO_PLAY_NO_OUT = "hit_into_play_no_out"
    HIT_INTO_PLAY_SCORE = "hit_into_play_score"

    # Play outcomes
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    FIELD_OUT = "field_out"
    STRIKEOUT = "strikeout"
    WALK = "walk"
    FORCE_OUT = "force_out"
    SAC_FLY = "sac_fly"
    GROUNDED_INTO_DOUBLE_PLAY = "grounded_into_double_play"
    CAUGHT_STEALING_2B = "caught_stealing_2b"

    # Substitutions and other
    AT_BAT_START = "at_bat_start"
    PITCHING_SUBSTITUTION = "pitching_substitution"
    OFFENSIVE_SUBSTITUTION = "offensive_substitution"
    DEFENSIVE_SWITCH = "defensive_switch"
    BATTER_TIMEOUT = "batter_timeout"
    MOUND_VISIT = "mound_visit"
    GAME_ADVISORY = "game_advisory"


# ---------------------------------------------------------------------------
# WebSocket message model
# ---------------------------------------------------------------------------


class ChangeEvent(MlbBaseModel):
    """Describes the type of change that triggered the push notification.

    Known ``type`` values: ``new_entry``, ``full_refresh``, ``correction``.
    Correction events may include ``changed_at_bat_indexes`` indicating
    which at-bats were modified.
    """

    type: str | None = None
    changed_at_bat_indexes: list[int] = []


class WsMessage(MlbBaseModel):
    """A single WebSocket push notification from the gameday feed.

    Example payload::

        {
            "timeStamp": "20230721_182018",
            "gamePk": "717325",
            "updateId": "7a5b0181-f833-4de8-bf1b-65de5e3ef6a3",
            "wait": 10,
            "logicalEvents": ["countChange", "count10", "basesEmpty"],
            "gameEvents": ["ball"],
            "changeEvent": {"type": "new_entry"},
        }
    """

    time_stamp: str
    game_pk: str
    update_id: str | None = None
    wait: int = 10
    logical_events: list[WsLogicalEvent | str] = []
    game_events: list[WsGameEvent | str] = []
    change_event: ChangeEvent | None = None
    is_delay: bool | None = None
