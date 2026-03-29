from __future__ import annotations


class MlbApiError(Exception):
    """Raised when the MLB Stats API returns an error response."""

    def __init__(self, status_code: int, message: str, url: str) -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code} from {url}: {message}")


class MlbValidationError(Exception):
    """Raised when an API response fails Pydantic validation."""

    def __init__(self, message: str, raw_data: dict[str, object] | None = None) -> None:
        self.raw_data = raw_data
        super().__init__(message)
