"""Pydantic v2 typed client for the MLB Stats API."""

from importlib.metadata import PackageNotFoundError, version

from mlb_statsapi.client.async_client import AsyncMlbClient
from mlb_statsapi.client.live import (
    FetchGranularity,
    GameEvent,
    GameEventData,
    LiveGameClient,
    LiveGameConfig,
    SyncLiveGameClient,
)
from mlb_statsapi.client.sync_client import MlbClient
from mlb_statsapi.exceptions import MlbApiError, MlbValidationError

try:
    __version__ = version("mlb-statsapi-pydantic")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"

__all__ = [
    "AsyncMlbClient",
    "FetchGranularity",
    "GameEvent",
    "GameEventData",
    "LiveGameClient",
    "LiveGameConfig",
    "MlbApiError",
    "MlbClient",
    "MlbValidationError",
    "SyncLiveGameClient",
    "__version__",
]
