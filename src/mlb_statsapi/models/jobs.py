"""Jobs models (umpires, official scorers, etc.)."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, MlbBaseModel, PersonRef

# Backwards-compatible alias
JobPerson = PersonRef


class JobEntry(MlbBaseModel):
    person: PersonRef | None = None
    jersey_number: str | None = None
    job: str | None = None
    job_id: str | None = None
    title: str | None = None


class JobsResponse(BaseResponse):
    roster: list[JobEntry] = []
