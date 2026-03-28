"""Jobs models (umpires, official scorers, etc.)."""

from __future__ import annotations

from mlb_statsapi.models._base import ListResponse, MlbBaseModel, PersonRef


class JobEntry(MlbBaseModel):
    person: PersonRef | None = None
    jersey_number: str | None = None
    job: str | None = None
    job_id: str | None = None
    title: str | None = None


class JobsResponse(ListResponse[JobEntry], items_field="roster"):
    roster: list[JobEntry] = []
