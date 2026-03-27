"""Jobs models (umpires, official scorers, etc.)."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, MlbBaseModel


class JobPerson(MlbBaseModel):
    id: int
    full_name: str
    link: str


class JobEntry(MlbBaseModel):
    person: JobPerson | None = None
    jersey_number: str | None = None
    job: str | None = None
    job_id: str | None = None
    title: str | None = None


class JobsResponse(BaseResponse):
    roster: list[JobEntry] = []
