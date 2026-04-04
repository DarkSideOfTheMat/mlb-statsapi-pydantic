"""Shared client logic — URL building, param validation, response parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

if TYPE_CHECKING:
    from pydantic import BaseModel

from mlb_statsapi.endpoints.registry import ENDPOINTS, EndpointDef
from mlb_statsapi.exceptions import MlbApiError, MlbValidationError
from mlb_statsapi.models._base import BaseResponse


class ClientMixin:
    """Non-I/O logic shared by sync and async clients."""

    @staticmethod
    def _hydrate_value(hydrate: str | list[str] | None) -> str | None:
        """Convert hydrate parameter to comma-separated string."""
        if hydrate is None:
            return None
        return ",".join(hydrate) if isinstance(hydrate, list) else hydrate

    def _resolve_endpoint(self, endpoint: str) -> EndpointDef:
        try:
            return ENDPOINTS[endpoint]
        except KeyError:
            raise MlbApiError(0, f"Unknown endpoint: {endpoint}", "") from None

    def _build_request(
        self, endpoint: str, **params: Any
    ) -> tuple[str, dict[str, str]]:
        ep = self._resolve_endpoint(endpoint)

        # Validate required params before making the request.
        # required_params is a tuple of groups — at least one group must be
        # fully satisfied (OR between groups, AND within each group).
        # An empty group ((),) means no params are required.
        if ep.required_params and not any(
            all(p in params for p in group) for group in ep.required_params
        ):
            groups_str = " OR ".join(
                "(" + ", ".join(g) + ")" for g in ep.required_params if g
            )
            raise MlbApiError(
                0,
                f"Missing required parameters for '{endpoint}': "
                f"must provide {groups_str}",
                "",
            )

        # Separate path params from query params
        path_params = {
            k: str(params.pop(k))
            for k in list(params)
            if k in ep.path_params or k == "ver"
        }
        url = ep.build_url(**path_params)
        query = ep.filter_query_params(**params)
        return url, query

    def _parse_response(self, endpoint: str, data: Any) -> BaseModel:
        ep = self._resolve_endpoint(endpoint)
        model = ep.response_model or BaseResponse
        try:
            return model.model_validate(data)
        except ValidationError as e:
            raise MlbValidationError(str(e), raw_data=data) from e
