"""Shared client logic — URL building, param validation, response parsing."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from mlb_statsapi.endpoints.registry import ENDPOINTS, EndpointDef
from mlb_statsapi.exceptions import MlbApiError, MlbValidationError
from mlb_statsapi.models._base import BaseResponse


class ClientMixin:
    """Non-I/O logic shared by sync and async clients."""

    def _resolve_endpoint(self, endpoint: str) -> EndpointDef:
        try:
            return ENDPOINTS[endpoint]
        except KeyError:
            raise MlbApiError(0, f"Unknown endpoint: {endpoint}", "") from None

    def _build_request(
        self, endpoint: str, **params: Any
    ) -> tuple[str, dict[str, str]]:
        ep = self._resolve_endpoint(endpoint)
        # Separate path params from query params
        path_params = {
            k: str(params.pop(k))
            for k in list(params)
            if k in ep.path_params or k == "ver"
        }
        url = ep.build_url(**path_params)
        query = ep.filter_query_params(**params)
        return url, query

    def _parse_response(self, endpoint: str, data: dict[str, Any]) -> BaseResponse:
        ep = self._resolve_endpoint(endpoint)
        model = ep.response_model or BaseResponse
        try:
            return model.model_validate(data)
        except ValidationError as e:
            raise MlbValidationError(str(e), raw_data=data) from e
