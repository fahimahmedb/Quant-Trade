"""The closed Form 4 population, as a predicate.

``governance/D07_OPEN_SPACE_BOUNDARY.md`` section 2.1 closes the population and
puts it outside D07 entirely:

* original Form 4 only (an amendment is not an original filing);
* non-derivative transaction;
* transaction code ``P``;
* acquired/disposed indicator ``A`` — **not** transaction code ``A``;
* qualifying reporting owner = director and/or officer;
* 10% ownership alone is insufficient; a 10% owner who is also an officer or
  director qualifies through that role;
* issuer identity = issuer CIK, insider identity = reporting-owner CIK;
* no fuzzy name matching.

The notation trap is the one worth a test: Form 4 transaction code ``A`` means an
award or grant, while the acquired/disposed indicator ``A`` means shares were
acquired. A qualifying purchase is code ``P`` *with* indicator ``A``. Treating
code ``A`` as qualifying would pool compensation grants into a conviction-buying
population, which is the single easiest way to get a large and meaningless sample.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ..dataplane.form4_parse import Form4Facts, Form4Transaction, ReportingOwner


#: Closed by D07 section 2.1.
QUALIFYING_TRANSACTION_CODE = "P"
QUALIFYING_ACQUIRED_INDICATOR = "A"


def qualifying_owner(owner: ReportingOwner) -> bool:
    """Director and/or officer. Ten-percent status alone does not qualify."""
    return bool(owner.is_director) or bool(owner.is_officer)


def qualifying_transaction(transaction: Form4Transaction) -> bool:
    """Non-derivative, code ``P``, acquired indicator ``A``."""
    return (not transaction.derivative
            and transaction.transaction_code == QUALIFYING_TRANSACTION_CODE
            and transaction.acquired_disposed == QUALIFYING_ACQUIRED_INDICATOR)


@dataclass(frozen=True)
class QualifyingEvent:
    """One qualifying (issuer, insider, transaction) triple from one filing."""

    issuer_cik: str
    owner_cik: str
    transaction_date: str | None
    shares: float | None
    price_per_share: float | None
    price_state: str
    officer: bool
    director: bool
    ten_percent_owner: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def qualifying_events(facts: Form4Facts) -> tuple[tuple[QualifyingEvent, ...], list[str]]:
    """Extract qualifying events from parsed facts, with the reasons for refusal.

    Returns ``(events, reasons)``. ``reasons`` is non-empty whenever the filing as
    a whole is excluded, so an exclusion leaves as much evidence as an inclusion.
    """
    reasons: list[str] = []
    if not facts.parsed:
        return (), [facts.state]
    if facts.is_amendment:
        reasons.append("ORIGINAL_FORM_4_ONLY_AMENDMENT_EXCLUDED")
    if facts.issuer_cik is None:
        reasons.append("ISSUER_CIK_ABSENT")
    owners = [owner for owner in facts.owners if qualifying_owner(owner)]
    if not owners:
        reasons.append("NO_QUALIFYING_REPORTING_OWNER")
    for owner in facts.owners:
        if owner.cik is None:
            reasons.append("REPORTING_OWNER_CIK_ABSENT")
        elif not owner.relationship_declared:
            reasons.append("REPORTING_OWNER_RELATIONSHIP_UNDECLARED")
    transactions = [row for row in facts.transactions if qualifying_transaction(row)]
    if not transactions:
        reasons.append("NO_QUALIFYING_TRANSACTION")
    if reasons:
        return (), sorted(set(reasons))

    events = tuple(
        QualifyingEvent(issuer_cik=str(facts.issuer_cik), owner_cik=str(owner.cik),
                        transaction_date=transaction.transaction_date,
                        shares=transaction.shares,
                        price_per_share=transaction.price_per_share,
                        price_state=transaction.price_state,
                        officer=bool(owner.is_officer), director=bool(owner.is_director),
                        ten_percent_owner=bool(owner.is_ten_percent_owner))
        for owner in owners for transaction in transactions)
    return events, []
