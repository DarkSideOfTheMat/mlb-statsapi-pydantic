"""Enum types for MLB Stats API fields."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport of StrEnum for Python < 3.11."""


class GameType(StrEnum):
    """Type of game (regular season, postseason, etc.)."""

    REGULAR_SEASON = "R"
    SPRING_TRAINING = "S"
    WILD_CARD = "F"
    DIVISION_SERIES = "D"
    LEAGUE_CHAMPIONSHIP = "L"
    WORLD_SERIES = "W"
    CHAMPIONSHIP = "C"
    PLAYOFFS = "P"
    ALL_STAR = "A"
    EXHIBITION = "E"
    INTRASQUAD = "I"


class AbstractGameState(StrEnum):
    """High-level game state."""

    PREVIEW = "Preview"
    LIVE = "Live"
    FINAL = "Final"


class HandCode(StrEnum):
    """Bat side or pitch hand code."""

    LEFT = "L"
    RIGHT = "R"
    SWITCH = "S"


class PositionType(StrEnum):
    """Player position category."""

    PITCHER = "Pitcher"
    CATCHER = "Catcher"
    INFIELDER = "Infielder"
    OUTFIELDER = "Outfielder"
    HITTER = "Hitter"
    RUNNER = "Runner"
    TWO_WAY_PLAYER = "Two-Way Player"
