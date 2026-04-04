"""Response models for game endpoints that lack dedicated modules.

This module provides response models for the following endpoints:

- ``/api/v1/game/{gamePk}/winProbability`` → :class:`WinProbabilityResponse`
- ``/api/v1/game/{gamePk}/contextMetrics`` → :class:`ContextMetricsResponse`
- ``/api/v1/game/{gamePk}/feed/live/timestamps`` → :class:`TimestampsResponse`
- ``/api/v1/game/{gamePk}/feed/color/timestamps`` → :class:`TimestampsResponse`
- ``/api/v1/game/changes`` → :class:`GameChangesResponse`
- ``/api/v1/game/{gamePk}/content`` → :class:`GameContentResponse`
- ``/api/v1/game/{gamePk}/feed/color`` → :class:`ColorFeedResponse`
- ``/api/v1/uniforms/game`` → :class:`UniformsResponse`

Models that inherit from :class:`MlbBaseModel` (rather than
:class:`BaseResponse`) indicate that the API response does not include
the standard ``copyright`` wrapper.
"""

from __future__ import annotations

from pydantic import RootModel

from mlb_statsapi.models._base import BaseResponse, GamePk, MlbBaseModel
from mlb_statsapi.models.livefeed import Play

# ---------------------------------------------------------------------------
# Win probability — /game/{gamePk}/winProbability
# ---------------------------------------------------------------------------


class WinProbabilityResponse(RootModel[list[Play]]):
    """Response from ``/api/v1/game/{gamePk}/winProbability``.

    Returns a JSON array of :class:`~mlb_statsapi.models.livefeed.Play`
    objects, each augmented with win-probability fields
    (``home_team_win_probability``, ``away_team_win_probability``,
    ``home_team_win_probability_added``).

    .. note::
        This endpoint returns a raw JSON array, not the standard
        ``{copyright, ...}`` wrapper used by most endpoints.
    """


# ---------------------------------------------------------------------------
# Context metrics — /game/{gamePk}/contextMetrics
# ---------------------------------------------------------------------------


class ContextMetricsResponse(MlbBaseModel):
    """Response from ``/api/v1/game/{gamePk}/contextMetrics``.

    Contains game-level win probabilities and sac-fly probabilities
    by outfield zone.

    .. note::
        This endpoint does not include a ``copyright`` field.
    """

    game: MlbBaseModel | None = None
    away_win_probability: float | None = None
    home_win_probability: float | None = None
    left_field_sac_fly_probability: MlbBaseModel | None = None
    center_field_sac_fly_probability: MlbBaseModel | None = None
    right_field_sac_fly_probability: MlbBaseModel | None = None


# ---------------------------------------------------------------------------
# Timestamps — /game/{gamePk}/feed/live/timestamps
#              /game/{gamePk}/feed/color/timestamps
# ---------------------------------------------------------------------------


class TimestampsResponse(RootModel[list[str]]):
    """Response from game timestamp endpoints.

    Returns a list of timecode strings (e.g. ``"20240605_200600"``).
    Used by both ``game_timestamps`` and ``game_color_timestamps``.

    .. note::
        This endpoint returns a raw JSON array, not the standard
        ``{copyright, ...}`` wrapper used by most endpoints.
    """


# ---------------------------------------------------------------------------
# Game changes — /game/changes
# ---------------------------------------------------------------------------


class GameChangesResponse(BaseResponse):
    """Response from ``/api/v1/game/changes``.

    Returns schedule-like data for games updated since a given timestamp.
    """

    total_items: int | None = None
    total_events: int | None = None
    total_games: int | None = None
    total_games_in_progress: int | None = None
    dates: list[MlbBaseModel] = []


# ---------------------------------------------------------------------------
# Game content — /game/{gamePk}/content
# ---------------------------------------------------------------------------


class MediaPlayback(MlbBaseModel):
    """A single media playback (video/audio) with resolution info."""

    name: str | None = None
    url: str | None = None
    width: str | None = None
    height: str | None = None


class MediaImage(MlbBaseModel):
    """Image metadata with template URL and cuts."""

    title: str | None = None
    alt_text: str | None = None
    template_url: str | None = None
    cuts: list[MlbBaseModel] | MlbBaseModel | None = None


class ContentItem(MlbBaseModel):
    """A media, highlight, or editorial content item.

    Used across highlights, editorial, and media sections of
    the game content response.
    """

    type: str | None = None
    state: str | None = None
    date: str | None = None
    id: str | int | None = None
    headline: str | None = None
    seo_title: str | None = None
    slug: str | None = None
    blurb: str | None = None
    title: str | None = None
    description: str | None = None
    duration: str | None = None
    media_playback_id: str | None = None
    media_playback_url: str | None = None
    image: MediaImage | None = None
    playbacks: list[MediaPlayback] = []
    keywords_all: list[MlbBaseModel] = []
    keywords_display: list[MlbBaseModel] = []
    no_index: bool | None = None


class ContentCollection(MlbBaseModel):
    """A named collection of content items (e.g. ``highlights.highlights``)."""

    items: list[ContentItem] = []


class EpgItem(MlbBaseModel):
    """Electronic program guide entry (broadcast info)."""

    title: str | None = None
    items: list[MlbBaseModel] = []


class GameContentMedia(MlbBaseModel):
    """Media section of game content (broadcasts, milestones, etc.)."""

    epg: list[EpgItem] = []
    epg_alternate: list[EpgItem] = []
    milestones: MlbBaseModel | None = None
    featured_media: MlbBaseModel | None = None
    free_game: bool | MlbBaseModel | None = None
    enhanced_game: bool | MlbBaseModel | None = None
    preview_story: MlbBaseModel | None = None


class GameContentHighlights(MlbBaseModel):
    """Highlights section of game content."""

    scoreboard: ContentCollection | None = None
    game_center: ContentCollection | None = None
    milestone: ContentCollection | None = None
    highlights: ContentCollection | None = None
    live: ContentCollection | None = None
    scoreboard_preview: ContentCollection | None = None


class GameContentEditorial(MlbBaseModel):
    """Editorial section (preview, recap, wrap articles)."""

    preview: MlbBaseModel | None = None
    articles: MlbBaseModel | None = None
    recap: MlbBaseModel | None = None
    wrap: MlbBaseModel | None = None


class GameContentResponse(BaseResponse):
    """Response from ``/api/v1/game/{gamePk}/content``.

    Contains media (broadcasts), highlights (video clips), and
    editorial content (preview/recap articles) for a game.
    """

    link: str | None = None
    editorial: GameContentEditorial | None = None
    media: GameContentMedia | None = None
    highlights: GameContentHighlights | None = None
    summary: MlbBaseModel | None = None
    game_notes: MlbBaseModel | None = None


# ---------------------------------------------------------------------------
# Color feed — /game/{gamePk}/feed/color
# ---------------------------------------------------------------------------


class ColorFeedItem(MlbBaseModel):
    """A single item in the color feed.

    Color feed items vary widely in structure; ``extra="allow"``
    on the base model captures all fields.
    """

    type: str | None = None


class ColorFeedResponse(MlbBaseModel):
    """Response from ``/api/v1/game/{gamePk}/feed/color``.

    .. note::
        This endpoint may return 404 for older games and does not
        include a ``copyright`` field.
    """

    items: list[ColorFeedItem] = []


# ---------------------------------------------------------------------------
# Uniforms — /uniforms/game
# ---------------------------------------------------------------------------


class UniformAsset(MlbBaseModel):
    """A single uniform asset (jersey, cap, helmet, etc.)."""

    uniform_asset_id: int | None = None
    uniform_asset_code: str | None = None
    uniform_asset_text: str | None = None
    uniform_asset_type: MlbBaseModel | str | None = None
    active: bool | None = None


class UniformTeam(MlbBaseModel):
    """Uniform info for one team in a game."""

    id: int | None = None
    team_name: str | None = None
    uniform_assets: list[UniformAsset] = []
    link: str | None = None


class GameUniforms(MlbBaseModel):
    """Uniform data for a single game."""

    game_pk: GamePk | None = None
    home: UniformTeam | None = None
    away: UniformTeam | None = None


class UniformsResponse(BaseResponse):
    """Response from ``/api/v1/uniforms/game``."""

    uniforms: list[GameUniforms] = []
