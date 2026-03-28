"""Transaction models."""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import BaseResponse, IdNameLink, MlbBaseModel, PersonRef
from mlb_statsapi.models.enums import TransactionType


class Transaction(MlbBaseModel):
    id: int
    person: PersonRef | None = None
    from_team: IdNameLink | None = None
    to_team: IdNameLink | None = None
    date: datetime.date | None = None
    effective_date: datetime.date | None = None
    resolution_date: datetime.date | None = None
    type_code: TransactionType | str | None = None
    type_desc: str | None = None
    description: str | None = None


class TransactionsResponse(BaseResponse):
    transactions: list[Transaction] = []
