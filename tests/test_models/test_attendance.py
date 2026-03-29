"""Tests for attendance models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestAttendanceResponse:
    def test_records_list_not_empty(self):
        from mlb_statsapi.models.attendance import AttendanceResponse

        data = load_fixture("attendance")
        resp = AttendanceResponse.model_validate(data)
        assert len(resp.records) > 0

    def test_record_has_year_attendance_and_team(self):
        from mlb_statsapi.models.attendance import AttendanceResponse

        data = load_fixture("attendance")
        resp = AttendanceResponse.model_validate(data)
        record = resp.records[0]
        assert record.year is not None
        assert record.attendance_total is not None
        assert record.team is not None

    def test_aggregate_totals_exists(self):
        from mlb_statsapi.models.attendance import AttendanceResponse

        data = load_fixture("attendance")
        resp = AttendanceResponse.model_validate(data)
        assert resp.aggregate_totals is not None
        assert resp.aggregate_totals.attendance_total is not None
