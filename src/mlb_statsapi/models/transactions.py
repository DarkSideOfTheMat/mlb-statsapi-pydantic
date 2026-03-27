"""Transaction models."""

from __future__ import annotations

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel


class TransactionPerson(MlbBaseModel):
    id: int
    full_name: str
    link: str


class Transaction(MlbBaseModel):
    id: int
    person: TransactionPerson | None = None
    from_team: IdNameLink | None = None
    to_team: IdNameLink | None = None
    date: str | None = None
    effective_date: str | None = None
    resolution_date: str | None = None
    type_code: str | None = None
    type_desc: str | None = None
    description: str | None = None


class TransactionsResponse(BaseResponse):
    transactions: list[Transaction] = []
