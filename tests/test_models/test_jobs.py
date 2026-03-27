"""Tests for jobs models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestJobsResponse:
    def test_roster_not_empty(self):
        from mlb_statsapi.models.jobs import JobsResponse

        data = load_fixture("jobs")
        resp = JobsResponse.model_validate(data)
        assert len(resp.roster) > 0

    def test_entry_has_person_jersey_and_title(self):
        from mlb_statsapi.models.jobs import JobsResponse

        data = load_fixture("jobs")
        resp = JobsResponse.model_validate(data)
        entry = resp.roster[0]
        assert entry.person is not None
        assert entry.person.full_name is not None
        assert entry.jersey_number is not None
        assert entry.title is not None
