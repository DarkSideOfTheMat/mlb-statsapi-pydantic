"""Jobs models (umpires, official scorers, datacasters, etc.).

Endpoint: ``/api/v1/jobs/umpires``, ``/api/v1/jobs/officialScorers``,
``/api/v1/jobs/datacasters``

Jobs represent personnel assignments for games, including umpires,
official scorers, and datacasters.
"""

from __future__ import annotations

from mlb_statsapi.models._base import ListResponse, MlbBaseModel, PersonRef


class JobEntry(MlbBaseModel):
    """A job assignment for a person.

    Contains the person reference, their job type, and optional
    jersey number and title.
    """

    person: PersonRef | None = None
    jersey_number: str | None = None
    job: str | None = None
    job_id: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None


class JobsResponse(ListResponse[JobEntry], items_field="roster"):
    """Response from ``/api/v1/jobs/*``."""

    roster: list[JobEntry] = []
