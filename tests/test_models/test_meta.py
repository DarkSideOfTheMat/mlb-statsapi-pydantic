"""Tests for meta models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestMetaItem:
    def test_validate_each_item(self):
        from mlb_statsapi.models.meta import MetaItem

        data = load_fixture("meta_game_types")
        items = [MetaItem.model_validate(item) for item in data]
        assert len(items) > 0

    def test_items_have_id_and_description(self):
        from mlb_statsapi.models.meta import MetaItem

        data = load_fixture("meta_game_types")
        for raw in data:
            item = MetaItem.model_validate(raw)
            assert item.id is not None
            assert item.description is not None
