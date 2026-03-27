"""Tests for draft models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestDraftResponse:
    def test_drafts_has_draft_year_and_rounds(self):
        from mlb_statsapi.models.draft import DraftResponse

        data = load_fixture("draft")
        resp = DraftResponse.model_validate(data)
        assert resp.drafts is not None
        assert resp.drafts.draft_year is not None
        assert len(resp.drafts.rounds) > 0

    def test_first_round_has_picks(self):
        from mlb_statsapi.models.draft import DraftResponse

        data = load_fixture("draft")
        resp = DraftResponse.model_validate(data)
        first_round = resp.drafts.rounds[0]
        assert len(first_round.picks) > 0

    def test_pick_has_person_and_team(self):
        from mlb_statsapi.models.draft import DraftResponse

        data = load_fixture("draft")
        resp = DraftResponse.model_validate(data)
        pick = resp.drafts.rounds[0].picks[0]
        assert pick.person is not None
        assert pick.person.full_name is not None
        assert pick.team is not None
