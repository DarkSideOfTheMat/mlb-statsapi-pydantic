"""Asynchronous MLB Stats API client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import httpx

from mlb_statsapi.client._base import ClientMixin
from mlb_statsapi.exceptions import MlbApiError

if TYPE_CHECKING:
    from pydantic import BaseModel
from mlb_statsapi.models.game import BoxscoreResponse, LinescoreResponse
from mlb_statsapi.models.game_responses import (
    ContextMetricsResponse,
    GameChangesResponse,
    GameContentResponse,
    TimestampsResponse,
    UniformsResponse,
    WinProbabilityResponse,
)
from mlb_statsapi.models.livefeed import LiveFeedResponse, PlayByPlayResponse
from mlb_statsapi.models.people import PeopleResponse
from mlb_statsapi.models.schedule import ScheduleResponse
from mlb_statsapi.models.sports import SportsResponse
from mlb_statsapi.models.standings import StandingsResponse
from mlb_statsapi.models.stats import StatsResponse
from mlb_statsapi.models.teams import TeamsResponse


class AsyncMlbClient(ClientMixin):
    """Asynchronous client for the MLB Stats API.

    Usage::

        async with AsyncMlbClient() as client:
            schedule = await client.schedule(sport_id=1, date="07/01/2024")
    """

    def __init__(self, timeout: float = 30.0) -> None:
        self._http = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncMlbClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def _request(self, endpoint: str, **params: Any) -> BaseModel:
        url, query = self._build_request(endpoint, **params)
        try:
            resp = await self._http.get(url, params=query)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise MlbApiError(e.response.status_code, str(e), url) from e
        except httpx.HTTPError as e:
            raise MlbApiError(0, str(e), url) from e
        return self._parse_response(endpoint, resp.json())

    # -- Generic access --

    async def get(self, endpoint: str, **params: Any) -> BaseModel:
        """Query any endpoint by name with automatic model parsing."""
        return await self._request(endpoint, **params)

    # -- Convenience methods --

    async def sports(self, **params: Any) -> SportsResponse:
        return cast(SportsResponse, await self._request("sports", **params))

    async def teams(
        self,
        sport_id: int = 1,
        hydrate: str | list[str] | None = None,
        **params: Any,
    ) -> TeamsResponse:
        kw: dict[str, Any] = {"sportId": sport_id, **params}
        if hydrate:
            kw["hydrate"] = self._hydrate_value(hydrate)
        return cast(TeamsResponse, await self._request("teams", **kw))

    async def team(
        self,
        team_id: int,
        hydrate: str | list[str] | None = None,
        **params: Any,
    ) -> TeamsResponse:
        kw: dict[str, Any] = {"teamId": str(team_id), **params}
        if hydrate:
            kw["hydrate"] = self._hydrate_value(hydrate)
        return cast(TeamsResponse, await self._request("team", **kw))

    async def person(
        self,
        person_id: int,
        hydrate: str | list[str] | None = None,
        **params: Any,
    ) -> PeopleResponse:
        kw: dict[str, Any] = {"personId": str(person_id), **params}
        if hydrate:
            kw["hydrate"] = self._hydrate_value(hydrate)
        return cast(PeopleResponse, await self._request("person", **kw))

    async def schedule(
        self,
        sport_id: int = 1,
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        team_id: int | None = None,
        hydrate: str | list[str] | None = None,
        **params: Any,
    ) -> ScheduleResponse:
        kw: dict[str, Any] = {"sportId": sport_id, **params}
        if date:
            kw["date"] = date
        if start_date:
            kw["startDate"] = start_date
        if end_date:
            kw["endDate"] = end_date
        if team_id:
            kw["teamId"] = team_id
        if hydrate:
            kw["hydrate"] = self._hydrate_value(hydrate)
        return cast(ScheduleResponse, await self._request("schedule", **kw))

    async def standings(
        self,
        league_id: str = "103,104",
        season: int | None = None,
        hydrate: str | list[str] | None = None,
        **params: Any,
    ) -> StandingsResponse:
        kw: dict[str, Any] = {"leagueId": league_id, **params}
        if season:
            kw["season"] = season
        if hydrate:
            kw["hydrate"] = self._hydrate_value(hydrate)
        return cast(StandingsResponse, await self._request("standings", **kw))

    async def game(self, game_pk: int, **params: Any) -> LiveFeedResponse:
        return cast(
            LiveFeedResponse, await self._request("game", gamePk=str(game_pk), **params)
        )

    async def boxscore(self, game_pk: int, **params: Any) -> BoxscoreResponse:
        return cast(
            BoxscoreResponse,
            await self._request("game_boxscore", gamePk=str(game_pk), **params),
        )

    async def linescore(self, game_pk: int, **params: Any) -> LinescoreResponse:
        return cast(
            LinescoreResponse,
            await self._request("game_linescore", gamePk=str(game_pk), **params),
        )

    async def play_by_play(self, game_pk: int, **params: Any) -> PlayByPlayResponse:
        return cast(
            PlayByPlayResponse,
            await self._request("game_playByPlay", gamePk=str(game_pk), **params),
        )

    async def win_probability(
        self, game_pk: int, **params: Any
    ) -> WinProbabilityResponse:
        return cast(
            WinProbabilityResponse,
            await self._request("game_winProbability", gamePk=str(game_pk), **params),
        )

    async def context_metrics(
        self, game_pk: int, **params: Any
    ) -> ContextMetricsResponse:
        return cast(
            ContextMetricsResponse,
            await self._request("game_contextMetrics", gamePk=str(game_pk), **params),
        )

    async def game_timestamps(self, game_pk: int, **params: Any) -> TimestampsResponse:
        return cast(
            TimestampsResponse,
            await self._request("game_timestamps", gamePk=str(game_pk), **params),
        )

    async def game_changes(
        self, updated_since: str, **params: Any
    ) -> GameChangesResponse:
        return cast(
            GameChangesResponse,
            await self._request("game_changes", updatedSince=updated_since, **params),
        )

    async def game_content(self, game_pk: int, **params: Any) -> GameContentResponse:
        return cast(
            GameContentResponse,
            await self._request("game_content", gamePk=str(game_pk), **params),
        )

    async def game_uniforms(self, game_pks: str, **params: Any) -> UniformsResponse:
        return cast(
            UniformsResponse,
            await self._request("game_uniforms", gamePks=game_pks, **params),
        )

    async def league_leaders(
        self,
        leader_categories: str = "homeRuns",
        season: int | None = None,
        sport_id: int = 1,
        limit: int = 10,
        hydrate: str | list[str] | None = None,
        **params: Any,
    ) -> StatsResponse:
        kw: dict[str, Any] = {
            "leaderCategories": leader_categories,
            "sportId": sport_id,
            "limit": limit,
            **params,
        }
        if season:
            kw["season"] = season
        if hydrate:
            kw["hydrate"] = self._hydrate_value(hydrate)
        return cast(StatsResponse, await self._request("stats_leaders", **kw))
