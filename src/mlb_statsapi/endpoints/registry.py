"""Endpoint registry for the MLB Stats API.

Ported from the reference library (toddrob99/MLB-StatsAPI) with typed
definitions linking each endpoint to its Pydantic response model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mlb_statsapi.models._base import BaseResponse

BASE_URL = "https://statsapi.mlb.com/api/"


@dataclass(frozen=True)
class EndpointDef:
    """Definition of a single MLB Stats API endpoint."""

    url_template: str
    path_params: dict[str, str] = field(default_factory=dict)
    query_params: tuple[str, ...] = ()
    required_params: tuple[tuple[str, ...], ...] = ((),)
    default_version: str = "v1"
    response_model: type[BaseResponse] | None = None
    note: str | None = None

    def build_url(self, **params: str) -> str:
        """Build the full URL with path parameters substituted."""
        ver = params.pop("ver", self.default_version)
        url = self.url_template.replace("{ver}", ver)

        for param, default in self.path_params.items():
            value = params.pop(param, default)
            url = url.replace("{" + param + "}", str(value) if value else "")

        # Clean up any double slashes from empty optional params
        while "//" in url:
            url = url.replace("//", "/")
        # Remove trailing slash
        url = url.rstrip("/")

        return BASE_URL + url

    def filter_query_params(self, **params: Any) -> dict[str, str]:
        """Filter params to only those accepted by this endpoint."""
        return {k: str(v) for k, v in params.items() if k in self.query_params}


def _build_endpoints() -> dict[str, EndpointDef]:
    """Build the full endpoint registry with response model links."""
    # Lazy imports to avoid circular dependencies
    from mlb_statsapi.models.divisions import DivisionsResponse
    from mlb_statsapi.models.game import BoxscoreResponse, LinescoreResponse
    from mlb_statsapi.models.leagues import LeaguesResponse
    from mlb_statsapi.models.livefeed import LiveFeedResponse
    from mlb_statsapi.models.people import PeopleResponse
    from mlb_statsapi.models.schedule import ScheduleResponse
    from mlb_statsapi.models.seasons import SeasonsResponse
    from mlb_statsapi.models.sports import SportsResponse
    from mlb_statsapi.models.standings import StandingsResponse
    from mlb_statsapi.models.stats import StatsResponse
    from mlb_statsapi.models.teams import TeamsResponse
    from mlb_statsapi.models.venues import VenuesResponse

    return {
        # --- Sports ---
        "sports": EndpointDef(
            url_template="{ver}/sports",
            query_params=("sportId", "fields"),
            response_model=SportsResponse,
        ),
        "sports_players": EndpointDef(
            url_template="{ver}/sports/{sportId}/players",
            path_params={"sportId": "1"},
            query_params=("season", "gameType", "fields"),
            required_params=(("season",),),
        ),
        # --- Teams ---
        "teams": EndpointDef(
            url_template="{ver}/teams",
            query_params=("season", "activeStatus", "leagueIds", "sportId", "sportIds", "gameType", "hydrate", "fields"),
            response_model=TeamsResponse,
        ),
        "team": EndpointDef(
            url_template="{ver}/teams/{teamId}",
            path_params={"teamId": ""},
            query_params=("season", "sportId", "hydrate", "fields"),
            response_model=TeamsResponse,
        ),
        "team_roster": EndpointDef(
            url_template="{ver}/teams/{teamId}/roster",
            path_params={"teamId": ""},
            query_params=("rosterType", "season", "date", "hydrate", "fields"),
        ),
        "team_stats": EndpointDef(
            url_template="{ver}/teams/{teamId}/stats",
            path_params={"teamId": ""},
            query_params=("season", "group", "gameType", "stats", "sportIds", "sitCodes", "fields"),
            required_params=(("season", "group"),),
        ),
        "team_coaches": EndpointDef(
            url_template="{ver}/teams/{teamId}/coaches",
            path_params={"teamId": ""},
            query_params=("season", "date", "fields"),
        ),
        "team_leaders": EndpointDef(
            url_template="{ver}/teams/{teamId}/leaders",
            path_params={"teamId": ""},
            query_params=("leaderCategories", "season", "leaderGameTypes", "hydrate", "limit", "fields"),
            required_params=(("leaderCategories", "season"),),
        ),
        "team_alumni": EndpointDef(
            url_template="{ver}/teams/{teamId}/alumni",
            path_params={"teamId": ""},
            query_params=("season", "group", "hydrate", "fields"),
            required_params=(("season", "group"),),
        ),
        "team_personnel": EndpointDef(
            url_template="{ver}/teams/{teamId}/personnel",
            path_params={"teamId": ""},
            query_params=("date", "fields"),
        ),
        "team_uniforms": EndpointDef(
            url_template="{ver}/uniforms/team",
            query_params=("teamIds", "season", "fields"),
            required_params=(("teamIds",),),
        ),
        "teams_history": EndpointDef(
            url_template="{ver}/teams/history",
            query_params=("teamIds", "startSeason", "endSeason", "fields"),
            required_params=(("teamIds",),),
        ),
        "teams_stats": EndpointDef(
            url_template="{ver}/teams/stats",
            query_params=("season", "sportIds", "group", "gameType", "stats", "order", "sortStat", "fields", "startDate", "endDate"),
            required_params=(("season", "group", "stats"),),
        ),
        "teams_affiliates": EndpointDef(
            url_template="{ver}/teams/affiliates",
            query_params=("teamIds", "sportId", "season", "hydrate", "fields"),
            required_params=(("teamIds",),),
        ),
        # --- People ---
        "people": EndpointDef(
            url_template="{ver}/people",
            query_params=("personIds", "hydrate", "fields"),
            required_params=(("personIds",),),
            response_model=PeopleResponse,
        ),
        "person": EndpointDef(
            url_template="{ver}/people/{personId}",
            path_params={"personId": ""},
            query_params=("hydrate", "fields"),
            response_model=PeopleResponse,
        ),
        "person_stats": EndpointDef(
            url_template="{ver}/people/{personId}/stats/game/{gamePk}",
            path_params={"personId": "", "gamePk": ""},
            query_params=("fields",),
        ),
        "people_changes": EndpointDef(
            url_template="{ver}/people/changes",
            query_params=("updatedSince", "fields"),
        ),
        "people_freeAgents": EndpointDef(
            url_template="{ver}/people/freeAgents",
            query_params=("order", "hydrate", "fields"),
        ),
        # --- Schedule ---
        "schedule": EndpointDef(
            url_template="{ver}/schedule",
            query_params=("scheduleType", "eventTypes", "hydrate", "teamId", "leagueId", "sportId", "gamePk", "gamePks", "venueIds", "gameTypes", "date", "startDate", "endDate", "opponentId", "fields", "season"),
            required_params=(("sportId",), ("gamePk",), ("gamePks",)),
            response_model=ScheduleResponse,
        ),
        "schedule_tied": EndpointDef(
            url_template="{ver}/schedule/games/tied",
            query_params=("gameTypes", "season", "hydrate", "fields"),
            required_params=(("season",),),
        ),
        "schedule_postseason": EndpointDef(
            url_template="{ver}/schedule/postseason",
            query_params=("gameTypes", "seriesNumber", "teamId", "sportId", "season", "hydrate", "fields"),
        ),
        "schedule_postseason_series": EndpointDef(
            url_template="{ver}/schedule/postseason/series",
            query_params=("gameTypes", "seriesNumber", "teamId", "sportId", "season", "fields"),
        ),
        # --- Standings ---
        "standings": EndpointDef(
            url_template="{ver}/standings",
            query_params=("leagueId", "season", "standingsTypes", "date", "hydrate", "fields"),
            required_params=(("leagueId",),),
            response_model=StandingsResponse,
        ),
        # --- Game ---
        "game": EndpointDef(
            url_template="{ver}/game/{gamePk}/feed/live",
            path_params={"gamePk": ""},
            query_params=("timecode", "hydrate", "fields"),
            default_version="v1.1",
            response_model=LiveFeedResponse,
        ),
        "game_boxscore": EndpointDef(
            url_template="{ver}/game/{gamePk}/boxscore",
            path_params={"gamePk": ""},
            query_params=("timecode", "fields"),
            response_model=BoxscoreResponse,
        ),
        "game_linescore": EndpointDef(
            url_template="{ver}/game/{gamePk}/linescore",
            path_params={"gamePk": ""},
            query_params=("timecode", "fields"),
            response_model=LinescoreResponse,
        ),
        "game_playByPlay": EndpointDef(
            url_template="{ver}/game/{gamePk}/playByPlay",
            path_params={"gamePk": ""},
            query_params=("timecode", "fields"),
        ),
        "game_content": EndpointDef(
            url_template="{ver}/game/{gamePk}/content",
            path_params={"gamePk": ""},
            query_params=("highlightLimit",),
        ),
        "game_diff": EndpointDef(
            url_template="{ver}/game/{gamePk}/feed/live/diffPatch",
            path_params={"gamePk": ""},
            query_params=("startTimecode", "endTimecode"),
            required_params=(("startTimecode", "endTimecode"),),
            default_version="v1.1",
        ),
        "game_timestamps": EndpointDef(
            url_template="{ver}/game/{gamePk}/feed/live/timestamps",
            path_params={"gamePk": ""},
            default_version="v1.1",
        ),
        "game_changes": EndpointDef(
            url_template="{ver}/game/changes",
            query_params=("updatedSince", "sportId", "gameType", "season", "fields"),
            required_params=(("updatedSince",),),
        ),
        "game_contextMetrics": EndpointDef(
            url_template="{ver}/game/{gamePk}/contextMetrics",
            path_params={"gamePk": ""},
            query_params=("timecode", "fields"),
        ),
        "game_winProbability": EndpointDef(
            url_template="{ver}/game/{gamePk}/winProbability",
            path_params={"gamePk": ""},
            query_params=("timecode", "fields"),
        ),
        "game_color": EndpointDef(
            url_template="{ver}/game/{gamePk}/feed/color",
            path_params={"gamePk": ""},
            query_params=("timecode", "fields"),
        ),
        "game_color_diff": EndpointDef(
            url_template="{ver}/game/{gamePk}/feed/color/diffPatch",
            path_params={"gamePk": ""},
            query_params=("startTimecode", "endTimecode"),
            required_params=(("startTimecode", "endTimecode"),),
        ),
        "game_color_timestamps": EndpointDef(
            url_template="{ver}/game/{gamePk}/feed/color/timestamps",
            path_params={"gamePk": ""},
        ),
        "game_uniforms": EndpointDef(
            url_template="{ver}/uniforms/game",
            query_params=("gamePks", "fields"),
            required_params=(("gamePks",),),
        ),
        # --- Stats ---
        "stats": EndpointDef(
            url_template="{ver}/stats",
            query_params=("stats", "playerPool", "position", "teamId", "leagueId", "limit", "offset", "group", "gameType", "season", "sportIds", "sortStat", "order", "hydrate", "fields", "personId", "metrics", "startDate", "endDate"),
            required_params=(("stats", "group"),),
        ),
        "stats_leaders": EndpointDef(
            url_template="{ver}/stats/leaders",
            query_params=("leaderCategories", "playerPool", "leaderGameTypes", "statGroup", "season", "leagueId", "sportId", "hydrate", "limit", "fields", "statType"),
            required_params=(("leaderCategories",),),
            response_model=StatsResponse,
        ),
        "stats_streaks": EndpointDef(
            url_template="{ver}/stats/streaks",
            query_params=("streakType", "streakSpan", "gameType", "season", "sportId", "limit", "hydrate", "fields"),
            required_params=(("streakType", "streakSpan", "season", "sportId", "limit"),),
        ),
        "gamePace": EndpointDef(
            url_template="{ver}/gamePace",
            query_params=("season", "teamIds", "leagueIds", "leagueListId", "sportId", "gameType", "startDate", "endDate", "venueIds", "orgType", "includeChildren", "fields"),
            required_params=(("season",),),
        ),
        "highLow": EndpointDef(
            url_template="{ver}/highLow/{orgType}",
            path_params={"orgType": ""},
            query_params=("statGroup", "sortStat", "season", "gameType", "teamId", "leagueId", "sportIds", "limit", "fields"),
            required_params=(("sortStat", "season"),),
        ),
        # --- Leagues ---
        "league": EndpointDef(
            url_template="{ver}/league",
            query_params=("sportId", "leagueIds", "seasons", "fields"),
            required_params=(("sportId",), ("leagueIds",)),
            response_model=LeaguesResponse,
        ),
        "league_allStarBallot": EndpointDef(
            url_template="{ver}/league/{leagueId}/allStarBallot",
            path_params={"leagueId": ""},
            query_params=("season", "fields"),
            required_params=(("season",),),
        ),
        "league_allStarWriteIns": EndpointDef(
            url_template="{ver}/league/{leagueId}/allStarWriteIns",
            path_params={"leagueId": ""},
            query_params=("season", "fields"),
            required_params=(("season",),),
        ),
        "league_allStarFinalVote": EndpointDef(
            url_template="{ver}/league/{leagueId}/allStarFinalVote",
            path_params={"leagueId": ""},
            query_params=("season", "fields"),
            required_params=(("season",),),
        ),
        # --- Divisions ---
        "divisions": EndpointDef(
            url_template="{ver}/divisions",
            query_params=("divisionId", "leagueId", "sportId", "season"),
            response_model=DivisionsResponse,
        ),
        # --- Seasons ---
        "seasons": EndpointDef(
            url_template="{ver}/seasons",
            query_params=("season", "sportId", "divisionId", "leagueId", "fields"),
            required_params=(("sportId",), ("divisionId",), ("leagueId",)),
            response_model=SeasonsResponse,
        ),
        "season": EndpointDef(
            url_template="{ver}/seasons/{seasonId}",
            path_params={"seasonId": ""},
            query_params=("sportId", "fields"),
            required_params=(("sportId",),),
        ),
        # --- Conferences ---
        "conferences": EndpointDef(
            url_template="{ver}/conferences",
            query_params=("conferenceId", "season", "fields"),
        ),
        # --- Venues ---
        "venue": EndpointDef(
            url_template="{ver}/venues",
            query_params=("venueIds", "season", "hydrate", "fields"),
            required_params=(("venueIds",),),
            response_model=VenuesResponse,
        ),
        # --- Awards ---
        "awards": EndpointDef(
            url_template="{ver}/awards",
            query_params=("sportId", "leagueId", "season", "hydrate", "fields"),
        ),
        # --- Draft ---
        "draft": EndpointDef(
            url_template="{ver}/draft",
            query_params=("limit", "fields", "round", "name", "school", "state", "country", "position", "teamId", "playerId", "bisPlayerId"),
        ),
        # --- Transactions ---
        "transactions": EndpointDef(
            url_template="{ver}/transactions",
            query_params=("teamId", "playerId", "date", "startDate", "endDate", "sportId", "fields"),
            required_params=(("teamId",), ("playerId",), ("date",), ("startDate", "endDate")),
        ),
        # --- Attendance ---
        "attendance": EndpointDef(
            url_template="{ver}/attendance",
            query_params=("teamId", "leagueId", "season", "date", "leagueListId", "gameType", "fields"),
            required_params=(("teamId",), ("leagueId",), ("leagueListId",)),
        ),
        # --- Home Run Derby ---
        "homeRunDerby": EndpointDef(
            url_template="{ver}/homeRunDerby/{gamePk}",
            path_params={"gamePk": ""},
            query_params=("fields",),
        ),
        # --- Jobs ---
        "jobs": EndpointDef(
            url_template="{ver}/jobs",
            query_params=("jobType", "sportId", "date", "fields"),
            required_params=(("jobType",),),
        ),
        "jobs_umpires": EndpointDef(
            url_template="{ver}/jobs/umpires",
            query_params=("sportId", "date", "fields"),
        ),
        "jobs_umpire_games": EndpointDef(
            url_template="{ver}/jobs/umpires/games/{umpireId}",
            path_params={"umpireId": ""},
            query_params=("season", "fields"),
            required_params=(("season",),),
        ),
        "jobs_datacasters": EndpointDef(
            url_template="{ver}/jobs/datacasters",
            query_params=("sportId", "date", "fields"),
        ),
        "jobs_officialScorers": EndpointDef(
            url_template="{ver}/jobs/officialScorers",
            query_params=("timecode", "fields"),
        ),
        # --- Meta ---
        "meta": EndpointDef(
            url_template="{ver}/{type}",
            path_params={"type": ""},
            note="Valid types: awards, baseballStats, eventTypes, gameStatus, gameTypes, hitTrajectories, jobTypes, languages, leagueLeaderTypes, logicalEvents, metrics, pitchCodes, pitchTypes, platforms, positions, reviewReasons, rosterTypes, scheduleEventTypes, situationCodes, sky, standingsTypes, statGroups, statTypes, windDirection.",
        ),
    }


ENDPOINTS: dict[str, EndpointDef] = _build_endpoints()
