"""Hard coded enums to use for convience

these could change in the future.
"""

from enum import Enum


class GAME_TYPES(str, Enum):
    SPRING_TRAINING = "S"
    REGULAR_SEASON = "R"
    WILD_CARD_GAME = "F"
    DIVISION_SERIES = "D"
    LEAGUE_CHAMPION_SERIES = "L"
    WORLD_SERIES = "W"
    CHAMPIONSHIP = "C"
    NINTEENTH_CENTURY_SERIES = "N"
    PLAYOFFS = "P"
    ALL_STAR_GAME = "A"
    INTRASQUAD = "I"
    EXHIBITION = "E"
