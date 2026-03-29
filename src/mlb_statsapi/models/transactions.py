"""Transaction models.

Endpoint: ``/api/v1/transactions``

Transactions record player movements between teams and status changes
(trades, signings, designations, waivers, etc.).
"""

from __future__ import annotations

import datetime

from mlb_statsapi.models._base import ListResponse, MlbBaseModel, PersonRef, Ref, TeamId
from mlb_statsapi.models.enums import TransactionType


class Transaction(MlbBaseModel):
    """A player transaction.

    Records a single roster move such as a trade, signing, option,
    designation for assignment, or status change. The ``type_code``
    identifies the transaction category.
    """

    id: int
    person: PersonRef | None = None
    from_team: Ref[TeamId] | None = None
    to_team: Ref[TeamId] | None = None
    date: datetime.date | None = None
    effective_date: datetime.date | None = None
    resolution_date: datetime.date | None = None
    type_code: TransactionType | str | None = None
    type_desc: str | None = None
    type: str | None = None
    description: str | None = None
    is_conditional: bool | None = None


class TransactionsResponse(ListResponse[Transaction], items_field="transactions"):
    """Response from ``/api/v1/transactions``."""

    transactions: list[Transaction] = []
