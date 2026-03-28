"""Enum types for MLB Stats API fields.

These enums document the known values returned by the API. All enum-typed
fields use the ``EnumType | str`` union pattern so that unexpected or
newly-added API values are accepted without breaking parsing.

Enum values were derived from the MLB Stats API meta endpoints
(``/api/v1/gameTypes``, ``/api/v1/eventTypes``, ``/api/v1/pitchCodes``,
``/api/v1/pitchTypes``, ``/api/v1/positions``, ``/api/v1/gameStatus``,
``/api/v1/standingsTypes``, ``/api/v1/transactionTypes``,
``/api/v1/hitTrajectories``, ``/api/v1/sky``, ``/api/v1/windDirection``,
``/api/v1/statGroups``, ``/api/v1/scheduleEventTypes``).
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport of StrEnum for Python < 3.11."""


# ---------------------------------------------------------------------------
# Game classification
# ---------------------------------------------------------------------------


class GameType(StrEnum):
    """Type of game (regular season, postseason, etc.).

    Source: ``/api/v1/gameTypes``
    """

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
    """High-level game state.

    Source: ``/api/v1/gameStatus`` (abstractGameState field)
    """

    PREVIEW = "Preview"
    LIVE = "Live"
    FINAL = "Final"


class CodedGameState(StrEnum):
    """Coded game state — a more granular state than AbstractGameState.

    Source: ``/api/v1/gameStatus`` (codedGameState field)
    """

    SCHEDULED = "S"
    PRE_GAME = "P"
    IN_PROGRESS = "I"
    MANAGER_CHALLENGE = "M"
    UMPIRE_REVIEW = "N"
    POSTPONED = "D"
    CANCELLED = "C"
    GAME_OVER = "O"
    FINAL = "F"
    SUSPENDED_IN_PROGRESS = "T"
    SUSPENDED_GAME_OVER = "U"
    FORFEIT_HOME = "Q"
    FORFEIT_AWAY = "R"
    UNKNOWN = "X"
    WRITING = "W"


class DetailedGameState(StrEnum):
    """Common detailed game states.

    The full set is very large (150+ codes with weather/reason variants).
    This enum covers the primary states. Use the ``status_code`` field
    for the complete code, or ``detailed_state`` for the human-readable text.

    Source: ``/api/v1/gameStatus`` (statusCode field)
    """

    SCHEDULED = "S"
    PRE_GAME = "P"
    WARMUP = "PW"
    IN_PROGRESS = "I"
    GAME_OVER = "O"
    FINAL = "F"
    POSTPONED = "DO"
    CANCELLED = "CO"
    SUSPENDED = "T"
    FORFEIT = "Q"


# ---------------------------------------------------------------------------
# Play-by-play
# ---------------------------------------------------------------------------


class HalfInning(StrEnum):
    """Half of an inning."""

    TOP = "top"
    BOTTOM = "bottom"


class EventType(StrEnum):
    """Play event type codes.

    Source: ``/api/v1/eventTypes``
    """

    # Hits
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    HOME_RUN = "home_run"
    # Outs
    FIELD_OUT = "field_out"
    STRIKEOUT = "strikeout"
    STRIKE_OUT = "strike_out"
    FORCE_OUT = "force_out"
    FIELDERS_CHOICE = "fielders_choice"
    FIELDERS_CHOICE_OUT = "fielders_choice_out"
    DOUBLE_PLAY = "double_play"
    GROUNDED_INTO_DOUBLE_PLAY = "grounded_into_double_play"
    GROUNDED_INTO_TRIPLE_PLAY = "grounded_into_triple_play"
    STRIKEOUT_DOUBLE_PLAY = "strikeout_double_play"
    STRIKEOUT_TRIPLE_PLAY = "strikeout_triple_play"
    TRIPLE_PLAY = "triple_play"
    SAC_FLY = "sac_fly"
    SAC_FLY_DOUBLE_PLAY = "sac_fly_double_play"
    SAC_BUNT = "sac_bunt"
    SAC_BUNT_DOUBLE_PLAY = "sac_bunt_double_play"
    FIELD_ERROR = "field_error"
    # Walks / HBP
    WALK = "walk"
    INTENT_WALK = "intent_walk"
    HIT_BY_PITCH = "hit_by_pitch"
    # Interference
    CATCHER_INTERF = "catcher_interf"
    BATTER_INTERFERENCE = "batter_interference"
    FIELDER_INTERFERENCE = "fielder_interference"
    RUNNER_INTERFERENCE = "runner_interference"
    FAN_INTERFERENCE = "fan_interference"
    # Baserunning
    STOLEN_BASE = "stolen_base"
    STOLEN_BASE_2B = "stolen_base_2b"
    STOLEN_BASE_3B = "stolen_base_3b"
    STOLEN_BASE_HOME = "stolen_base_home"
    CAUGHT_STEALING = "caught_stealing"
    CAUGHT_STEALING_2B = "caught_stealing_2b"
    CAUGHT_STEALING_3B = "caught_stealing_3b"
    CAUGHT_STEALING_HOME = "caught_stealing_home"
    PICKOFF_1B = "pickoff_1b"
    PICKOFF_2B = "pickoff_2b"
    PICKOFF_3B = "pickoff_3b"
    PICKOFF_ERROR_1B = "pickoff_error_1b"
    PICKOFF_ERROR_2B = "pickoff_error_2b"
    PICKOFF_ERROR_3B = "pickoff_error_3b"
    PICKOFF_CAUGHT_STEALING_2B = "pickoff_caught_stealing_2b"
    PICKOFF_CAUGHT_STEALING_3B = "pickoff_caught_stealing_3b"
    PICKOFF_CAUGHT_STEALING_HOME = "pickoff_caught_stealing_home"
    CS_DOUBLE_PLAY = "cs_double_play"
    RUNNER_DOUBLE_PLAY = "runner_double_play"
    RUNNER_PLACED = "runner_placed"
    PASSED_BALL = "passed_ball"
    WILD_PITCH = "wild_pitch"
    BALK = "balk"
    FORCED_BALK = "forced_balk"
    OTHER_ADVANCE = "other_advance"
    OTHER_OUT = "other_out"
    ERROR = "error"
    DEFENSIVE_INDIFF = "defensive_indiff"
    # Substitutions
    PITCHING_SUBSTITUTION = "pitching_substitution"
    OFFENSIVE_SUBSTITUTION = "offensive_substitution"
    DEFENSIVE_SUBSTITUTION = "defensive_substitution"
    DEFENSIVE_SWITCH = "defensive_switch"
    PITCHER_SWITCH = "pitcher_switch"
    UMPIRE_SUBSTITUTION = "umpire_substitution"
    # Other
    BATTER_TIMEOUT = "batter_timeout"
    PITCHER_STEP_OFF = "pitcher_step_off"
    MOUND_VISIT = "mound_visit"
    NO_PITCH = "no_pitch"
    GAME_ADVISORY = "game_advisory"
    INJURY = "injury"
    EJECTION = "ejection"
    BATTER_TURN = "batter_turn"
    AT_BAT_START = "at_bat_start"
    OS_RULING_PENDING_PRIOR = "os_ruling_pending_prior"
    OS_RULING_PENDING_PRIMARY = "os_ruling_pending_primary"


class PitchCode(StrEnum):
    """Pitch call result codes — the umpire's ruling on a pitch.

    Source: ``/api/v1/pitchCodes``
    """

    CALLED_STRIKE = "C"
    SWINGING_STRIKE = "S"
    SWINGING_STRIKE_BLOCKED = "W"
    FOUL = "F"
    FOUL_BUNT = "L"
    MISSED_BUNT = "M"
    FOUL_TIP = "T"
    FOUL_PITCHOUT = "R"
    BUNT_FOUL_TIP = "O"
    SWINGING_PITCHOUT = "Q"
    HIT_INTO_PLAY_OUT = "X"
    HIT_INTO_PLAY_NO_OUT = "D"
    HIT_INTO_PLAY_RUNS = "E"
    PITCHOUT_HIT_OUT = "Y"
    PITCHOUT_HIT_NO_OUT = "J"
    PITCHOUT_HIT_RUNS = "Z"
    BALL = "B"
    BALL_IN_DIRT = "*B"
    INTENTIONAL_BALL = "I"
    PITCHOUT = "P"
    HIT_BY_PITCH = "H"
    AUTOMATIC_STRIKE = "A"
    AUTOMATIC_STRIKE_PTV = "AC"
    AUTOMATIC_STRIKE_BTO = "AB"
    AUTOMATIC_BALL = "V"
    AUTOMATIC_BALL_PTV_CATCHER = "VC"
    AUTOMATIC_BALL_PTV_PITCHER = "VP"
    AUTOMATIC_BALL_IBB = "VB"
    AUTOMATIC_BALL_SHIFT = "VS"
    STRIKE_UNKNOWN = "K"
    NO_PITCH = "N"
    PITCHER_STEP_OFF = "PSO"
    PICKOFF_1B_PITCHER = "1"
    PICKOFF_2B_PITCHER = "2"
    PICKOFF_3B_PITCHER = "3"
    PICKOFF_1B_CATCHER = "+1"
    PICKOFF_2B_CATCHER = "+2"
    PICKOFF_3B_CATCHER = "+3"
    NON_PITCH = "."


class PitchType(StrEnum):
    """Pitch classification codes.

    Source: ``/api/v1/pitchTypes``
    """

    FASTBALL = "FA"
    FOUR_SEAM = "FF"
    TWO_SEAM = "FT"
    CUTTER = "FC"
    SPLITTER = "FS"
    FORKBALL = "FO"
    SINKER = "SI"
    SWEEPER = "ST"
    SLIDER = "SL"
    CURVEBALL = "CU"
    KNUCKLE_CURVE = "KC"
    SCREWBALL = "SC"
    GYROBALL = "GY"
    SLURVE = "SV"
    SLOW_CURVE = "CS"
    CHANGEUP = "CH"
    KNUCKLEBALL = "KN"
    EEPHUS = "EP"
    UNKNOWN = "UN"
    INTENTIONAL_BALL = "IN"
    PITCHOUT = "PO"
    AUTOMATIC_BALL = "AB"
    AUTOMATIC_STRIKE = "AS"
    NO_PITCH = "NP"


class HitTrajectory(StrEnum):
    """Batted ball trajectory classification.

    Source: ``/api/v1/hitTrajectories``
    """

    GROUND_BALL = "ground_ball"
    FLY_BALL = "fly_ball"
    LINE_DRIVE = "line_drive"
    POPUP = "popup"
    BUNT_GROUNDER = "bunt_grounder"
    BUNT_POPUP = "bunt_popup"
    BUNT_LINE_DRIVE = "bunt_line_drive"


class FieldingCredit(StrEnum):
    """Fielding credit types for runner events."""

    PUTOUT = "f_putout"
    ASSIST = "f_assist"
    FIELDED_BALL = "f_fielded_ball"
    DEFLECTION = "f_deflection"


# ---------------------------------------------------------------------------
# Player attributes
# ---------------------------------------------------------------------------


class HandCode(StrEnum):
    """Bat side or pitch hand code."""

    LEFT = "L"
    RIGHT = "R"
    SWITCH = "S"


class PositionType(StrEnum):
    """Player position category.

    Source: ``/api/v1/positions`` (type field)
    """

    PITCHER = "Pitcher"
    CATCHER = "Catcher"
    INFIELDER = "Infielder"
    OUTFIELDER = "Outfielder"
    HITTER = "Hitter"
    RUNNER = "Runner"
    TWO_WAY_PLAYER = "Two-Way Player"
    BATTER = "Batter"
    UNKNOWN = "Unknown"


class PositionAbbreviation(StrEnum):
    """Position abbreviations.

    Source: ``/api/v1/positions`` (abbrev field)
    """

    PITCHER = "P"
    CATCHER = "C"
    FIRST_BASE = "1B"
    SECOND_BASE = "2B"
    THIRD_BASE = "3B"
    SHORTSTOP = "SS"
    LEFT_FIELD = "LF"
    CENTER_FIELD = "CF"
    RIGHT_FIELD = "RF"
    DESIGNATED_HITTER = "DH"
    PINCH_HITTER = "PH"
    PINCH_RUNNER = "PR"
    EXTRA_HITTER = "EH"
    BASE_RUNNER = "BR"
    OUTFIELD = "OF"
    INFIELD = "IF"
    STARTING_PITCHER = "SP"
    RELIEF_PITCHER = "RP"
    CLOSER = "CP"
    UTILITY = "UT"
    UTILITY_INFIELDER = "UI"
    UTILITY_OUTFIELDER = "UO"
    RIGHT_HANDED_PITCHER = "RHP"
    LEFT_HANDED_PITCHER = "LHP"
    RIGHT_HANDED_STARTER = "RHS"
    LEFT_HANDED_STARTER = "LHS"
    LEFT_HANDED_RELIEVER = "LHR"
    RIGHT_HANDED_RELIEVER = "RHR"
    PITCHER_INFIELDER = "P-IF"
    PITCHER_OUTFIELDER = "P-OF"
    PITCHER_UTILITY = "P-UT"
    TWO_WAY_PLAYER = "TWP"
    BATTER = "B"
    UNKNOWN = "X"
    RUNNER_ON_FIRST = "R1"
    RUNNER_ON_SECOND = "R2"
    RUNNER_ON_THIRD = "R3"


# ---------------------------------------------------------------------------
# Game logistics
# ---------------------------------------------------------------------------


class DayNight(StrEnum):
    """Day/night game designation."""

    DAY = "day"
    NIGHT = "night"


class DoubleHeaderCode(StrEnum):
    """Doubleheader status code."""

    NOT_DOUBLEHEADER = "N"
    DOUBLEHEADER = "Y"
    SPLIT_DOUBLEHEADER = "S"


class TiebreakerCode(StrEnum):
    """Tiebreaker game designation."""

    NOT_TIEBREAKER = "N"
    TIEBREAKER = "Y"


# ---------------------------------------------------------------------------
# Standings
# ---------------------------------------------------------------------------


class StandingsType(StrEnum):
    """Type of standings view.

    Source: ``/api/v1/standingsTypes``
    """

    REGULAR_SEASON = "regularSeason"
    WILD_CARD = "wildCard"
    DIVISION_LEADERS = "divisionLeaders"
    WILD_CARD_WITH_LEADERS = "wildCardWithLeaders"
    FIRST_HALF = "firstHalf"
    SECOND_HALF = "secondHalf"
    SPRING_TRAINING = "springTraining"
    POSTSEASON = "postseason"
    BY_DIVISION = "byDivision"
    BY_CONFERENCE = "byConference"
    BY_LEAGUE = "byLeague"
    BY_ORGANIZATION = "byOrganization"
    CURRENT_HALF = "currentHalf"


class StreakType(StrEnum):
    """Win/loss streak type."""

    WINS = "wins"
    LOSSES = "losses"


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------


class TransactionType(StrEnum):
    """Transaction type codes.

    Source: ``/api/v1/transactionTypes``
    """

    STATUS_CHANGE = "SC"
    ASSIGNED = "ASG"
    DESIGNATED_FOR_ASSIGNMENT = "DES"
    OPTIONED = "OPT"
    OUTRIGHTED = "OUT"
    TRADE = "TR"
    DECLARED_FREE_AGENCY = "DFA"
    RELEASED = "REL"
    UNCONDITIONAL_RELEASE = "URL"
    WAIVED = "WA"
    RETIRED = "RET"
    SUSPENSION = "SU"
    DECLARED_INELIGIBLE = "DEI"
    RESERVED = "RES"
    DECEASED = "DEC"
    NUMBER_CHANGE = "NUM"
    CLAIMED_OFF_WAIVERS = "CLW"
    PURCHASE = "PUR"
    SIGNED = "SGN"
    SIGNED_FREE_AGENT = "SFA"
    DRAFTED = "DR"
    SELECTED = "SE"
    RECALLED = "CU"
    REINSTATED = "RE"
    NEW_CONTRACT = "NC"
    CONTRACT_PURCHASED = "CP"
    CONTRACT_VOID = "CV"
    OFFERED_ARBITRATION = "ARB"
    NOT_OFFERED_ARBITRATION = "NOA"
    REFUSED_ARBITRATION = "REF"
    NOT_TENDERED_CONTRACT = "NTC"
    LOAN = "LON"
    RETURNED = "RTN"
    AWARDED = "AWD"
    TRANSFERRED = "TRN"
    OBTAINED = "OBT"
    JUMPED = "JUM"
    RULE_5_SELECTION = "R5"
    RULE_5_DRAFT_MINORS = "R5M"


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


class StatGroup(StrEnum):
    """Statistical grouping category.

    Source: ``/api/v1/statGroups``
    """

    HITTING = "hitting"
    PITCHING = "pitching"
    FIELDING = "fielding"
    CATCHING = "catching"
    RUNNING = "running"
    GAME = "game"
    TEAM = "team"
    STREAK = "streak"


class StatType(StrEnum):
    """Common stat query types.

    Source: ``/api/v1/statTypes``
    """

    SEASON = "season"
    CAREER = "career"
    YEAR_BY_YEAR = "yearByYear"
    YEAR_BY_YEAR_ADVANCED = "yearByYearAdvanced"
    SEASON_ADVANCED = "seasonAdvanced"
    CAREER_ADVANCED = "careerAdvanced"
    GAME_LOG = "gameLog"
    PLAY_LOG = "playLog"
    PITCH_LOG = "pitchLog"
    VS_PLAYER = "vsPlayer"
    VS_TEAM = "vsTeam"
    LAST_X_GAMES = "lastXGames"
    BY_DATE_RANGE = "byDateRange"
    BY_MONTH = "byMonth"
    HOME_AND_AWAY = "homeAndAway"
    WIN_LOSS = "winLoss"
    RANKINGS = "rankings"
    HOT_COLD_ZONES = "hotColdZones"
    EXPECTED_STATISTICS = "expectedStatistics"
    SABERMETRICS = "sabermetrics"
    SPRAY_CHART = "sprayChart"
    TRACKING = "tracking"
    PITCH_ARSENAL = "pitchArsenal"
    PROJECTED = "projected"


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------


class Sky(StrEnum):
    """Sky/weather condition.

    Source: ``/api/v1/sky``
    """

    CLEAR = "Clear"
    CLOUDY = "Cloudy"
    DOME = "Dome"
    DRIZZLE = "Drizzle"
    OVERCAST = "Overcast"
    PARTLY_CLOUDY = "Partly Cloudy"
    RAIN = "Rain"
    ROOF_CLOSED = "Roof Closed"
    SNOW = "Snow"
    SUNNY = "Sunny"


class WindDirection(StrEnum):
    """Wind direction at the ballpark.

    Source: ``/api/v1/windDirection``
    """

    CALM = "Calm"
    IN_FROM_CF = "In From CF"
    IN_FROM_LF = "In From LF"
    IN_FROM_RF = "In From RF"
    L_TO_R = "L To R"
    NONE = "None"
    OUT_TO_CF = "Out To CF"
    OUT_TO_LF = "Out To LF"
    OUT_TO_RF = "Out To RF"
    R_TO_L = "R To L"
    VARIES = "Varies"


# ---------------------------------------------------------------------------
# Schedule event types
# ---------------------------------------------------------------------------


class ScheduleEventType(StrEnum):
    """Schedule event type codes.

    Source: ``/api/v1/scheduleEventTypes``
    """

    ALL_STAR_WEEKEND = "A"
    TEAM_EVENT = "T"
    EXHIBITION = "E"
    POSTSEASON_GAMES = "Z"
    SPRING_TRAINING_GAMES = "Y"
    PITCHERS_CATCHERS_REPORT = "W"
    FULL_SQUAD_REPORTS = "X"
    STH_EVENTS = "H"
    BALLPARK_TOURS = "B"
    IMPORTANT_DATES = "I"
    OTHER = "O"
    CULTURAL_EVENTS = "C"
    TRACKING_DATA = "D"
    FESTIVAL = "F"
    KIDS_FAMILY = "K"
    MUSIC = "M"
    PROMOTION_BACKGROUND = "P"
    PROMOTION_SINGLE_DATE = "Q"
    STUDIO_EVENT = "S"


# ---------------------------------------------------------------------------
# Roster types
# ---------------------------------------------------------------------------


class RosterType(StrEnum):
    """Roster type parameter values.

    Source: ``/api/v1/rosterTypes``
    """

    FORTY_MAN = "40Man"
    FULL_SEASON = "fullSeason"
    FULL_ROSTER = "fullRoster"
    NON_ROSTER_INVITEES = "nonRosterInvitees"
    ACTIVE = "active"
    ALL_TIME = "allTime"
    DEPTH_CHART = "depthChart"
    GAMEDAY = "gameday"
    COACH = "coach"
