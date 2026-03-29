"""Meta/enumeration models (gameTypes, positions, statTypes, etc.).

The meta endpoint returns bare lists, not wrapped responses.
"""

from __future__ import annotations

from mlb_statsapi.models._base import MlbBaseModel


class MetaItem(MlbBaseModel):
    """Generic meta item — covers gameTypes, positions, statTypes, etc."""

    id: str | None = None
    description: str | None = None
