"""Tests for transactions models."""

from __future__ import annotations

from tests.conftest import load_fixture


class TestTransactionsResponse:
    def test_transactions_list_not_empty(self):
        from mlb_statsapi.models.transactions import TransactionsResponse

        data = load_fixture("transactions")
        resp = TransactionsResponse.model_validate(data)
        assert len(resp.transactions) > 0

    def test_transaction_has_required_fields(self):
        from mlb_statsapi.models.transactions import TransactionsResponse

        data = load_fixture("transactions")
        resp = TransactionsResponse.model_validate(data)
        txn = resp.transactions[0]
        assert txn.id is not None
        assert txn.type_code is not None
        assert txn.type_desc is not None
        assert txn.description is not None

    def test_person_has_full_name(self):
        from mlb_statsapi.models.transactions import TransactionsResponse

        data = load_fixture("transactions")
        resp = TransactionsResponse.model_validate(data)
        txn = resp.transactions[0]
        assert txn.person is not None
        assert txn.person.full_name is not None
