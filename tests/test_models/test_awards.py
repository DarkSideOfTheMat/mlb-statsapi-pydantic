"""Tests for awards models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestAwardsResponse:
    def test_awards_list_not_empty(self):
        from mlb_statsapi.models.awards import AwardsResponse

        data = load_fixture("awards")
        resp = AwardsResponse.model_validate(data)
        assert len(resp.awards) > 0

    def test_first_award_has_id_and_name(self):
        from mlb_statsapi.models.awards import AwardsResponse

        data = load_fixture("awards")
        resp = AwardsResponse.model_validate(data)
        award = resp.awards[0]
        assert award.id is not None
        assert award.name is not None

    def test_some_awards_have_sport(self):
        from mlb_statsapi.models.awards import AwardsResponse

        data = load_fixture("awards")
        resp = AwardsResponse.model_validate(data)
        awards_with_sport = [a for a in resp.awards if a.sport is not None]
        assert len(awards_with_sport) > 0
        sport = awards_with_sport[0].sport
        assert sport.id is not None
