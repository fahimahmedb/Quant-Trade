"""Downstream Form 4 structure extraction — a pure function over bytes.

This module has no filesystem access, no network access and no knowledge of where
Form 4 documents are stored.  It converts one document's bytes into structured
facts, or into an explicit failure state.  It is deliberately unable to read the
P0 capture reservoir: callers hand it bytes, and during development those bytes
come from synthetic fixtures.

Three modelling decisions matter more than the parsing:

* **A grant is not a purchase.** Transaction code ``A`` (award) and code ``P``
  (open-market purchase) are economically different events. Research that pools
  them is measuring compensation schedules alongside conviction buying, so
  :attr:`Form4Transaction.is_open_market_purchase` is narrow on purpose.
* **A missing price is not zero.** Form 4 routinely puts a price range in a
  footnote. That is ``PRICE_IN_FOOTNOTE_NOT_MACHINE_READABLE``, not 0.0.
* **``periodOfReport`` is not when the market could know.** The document states
  when the transaction happened, never when the filing became publicly
  observable. The public-observability instant comes from the acceptance
  timestamp, which lives outside the document, so this parser refuses to supply
  one.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from xml.etree import ElementTree


PARSE_OK = "PARSE_OK"
PARSE_MALFORMED_XML = "PARSE_MALFORMED_XML"
PARSE_NOT_OWNERSHIP_DOCUMENT = "PARSE_NOT_OWNERSHIP_DOCUMENT"
PARSE_NOT_FORM_4 = "PARSE_NOT_FORM_4"
PARSE_DOCUMENT_TYPE_UNREADABLE = "PARSE_DOCUMENT_TYPE_UNREADABLE"

#: The public-observability instant is not derivable from the document.
PUBLIC_OBSERVABILITY_UNAVAILABLE = "PUBLIC_OBSERVABILITY_REQUIRES_ACCEPTANCE_TIMESTAMP"

PRICE_ABSENT = "PRICE_ABSENT"
PRICE_IN_FOOTNOTE = "PRICE_IN_FOOTNOTE_NOT_MACHINE_READABLE"
PRICE_PRESENT = "PRICE_PRESENT"

#: Transaction codes that are open-market or private purchases/sales for cash.
CODE_OPEN_MARKET_PURCHASE = "P"
CODE_OPEN_MARKET_SALE = "S"
#: Codes that are not discretionary market transactions.
NON_MARKET_CODES = ("A", "F", "G", "M", "C", "D", "I", "J", "L", "U", "W", "Z")


def _text(node: ElementTree.Element | None) -> str | None:
    if node is None:
        return None
    value = (node.text or "").strip()
    return value or None


def _value_of(parent: ElementTree.Element | None, tag: str) -> tuple[str | None, bool]:
    """Return ``(value, footnote_only)`` for a Form 4 ``<tag><value>`` pair."""
    if parent is None:
        return None, False
    node = parent.find(tag)
    if node is None:
        return None, False
    value = _text(node.find("value"))
    if value is not None:
        return value, False
    footnote = node.find("footnoteId") is not None
    return None, footnote


def _number(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def _flag(parent: ElementTree.Element | None, tag: str) -> bool | None:
    if parent is None:
        return None
    raw = _text(parent.find(tag))
    if raw is None:
        raw, _ = _value_of(parent, tag)
    if raw is None:
        return None
    return raw.strip() in ("1", "true", "TRUE", "True")


@dataclass(frozen=True)
class ReportingOwner:
    cik: str | None
    name: str | None
    is_director: bool | None = None
    is_officer: bool | None = None
    is_ten_percent_owner: bool | None = None
    is_other: bool | None = None
    officer_title: str | None = None

    @property
    def relationship_declared(self) -> bool:
        return any(flag is not None for flag in
                   (self.is_director, self.is_officer, self.is_ten_percent_owner,
                    self.is_other))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Form4Transaction:
    security_title: str | None
    transaction_date: str | None
    transaction_code: str | None
    acquired_disposed: str | None
    shares: float | None
    price_per_share: float | None
    price_state: str
    shares_owned_following: float | None = None
    direct_or_indirect: str | None = None
    derivative: bool = False
    equity_swap_involved: bool | None = None

    @property
    def is_open_market_purchase(self) -> bool:
        """Narrow by design: code P, acquired, non-derivative, price readable."""
        return (self.transaction_code == CODE_OPEN_MARKET_PURCHASE
                and self.acquired_disposed == "A"
                and not self.derivative
                and self.price_state == PRICE_PRESENT
                and (self.shares or 0.0) > 0)

    @property
    def is_open_market_sale(self) -> bool:
        return (self.transaction_code == CODE_OPEN_MARKET_SALE
                and self.acquired_disposed == "D"
                and not self.derivative
                and self.price_state == PRICE_PRESENT
                and (self.shares or 0.0) > 0)

    @property
    def notional(self) -> float | None:
        if self.shares is None or self.price_per_share is None:
            return None
        return self.shares * self.price_per_share

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.transaction_date is None:
            problems.append("TRANSACTION_DATE_ABSENT")
        if self.transaction_code is None:
            problems.append("TRANSACTION_CODE_ABSENT")
        if self.acquired_disposed not in ("A", "D", None):
            problems.append("ACQUIRED_DISPOSED_CODE_UNREADABLE")
        if self.shares is None:
            problems.append("SHARES_ABSENT")
        if self.price_state == PRICE_IN_FOOTNOTE:
            problems.append(PRICE_IN_FOOTNOTE)
        return problems

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["is_open_market_purchase"] = self.is_open_market_purchase
        document["is_open_market_sale"] = self.is_open_market_sale
        document["notional"] = self.notional
        return document


@dataclass(frozen=True)
class Form4Facts:
    """Structured content of one Form 4 document, with explicit unknowns."""

    state: str
    document_type: str | None = None
    period_of_report: str | None = None
    issuer_cik: str | None = None
    issuer_name: str | None = None
    issuer_trading_symbol: str | None = None
    owners: tuple[ReportingOwner, ...] = ()
    transactions: tuple[Form4Transaction, ...] = ()
    footnote_ids: tuple[str, ...] = ()
    is_amendment: bool = False
    detail: str = ""

    #: Always ``None``: the document cannot say when the market could know.
    public_observability_instant: None = None
    public_observability_state: str = PUBLIC_OBSERVABILITY_UNAVAILABLE

    @property
    def parsed(self) -> bool:
        return self.state == PARSE_OK

    @property
    def open_market_purchases(self) -> tuple[Form4Transaction, ...]:
        return tuple(row for row in self.transactions if row.is_open_market_purchase)

    def violations(self) -> list[str]:
        problems: list[str] = []
        if not self.parsed:
            return [self.state]
        if self.issuer_cik is None:
            problems.append("ISSUER_CIK_ABSENT")
        if not self.owners:
            problems.append("NO_REPORTING_OWNER")
        for owner in self.owners:
            if owner.cik is None:
                problems.append("REPORTING_OWNER_CIK_ABSENT")
            if not owner.relationship_declared:
                problems.append("REPORTING_OWNER_RELATIONSHIP_UNDECLARED")
        if not self.transactions:
            problems.append("NO_TRANSACTION_ROWS")
        for index, transaction in enumerate(self.transactions):
            problems.extend(f"transaction[{index}]: {problem}"
                            for problem in transaction.violations())
        if self.is_amendment:
            problems.append("AMENDMENT_SUPERSEDES_PRIOR_FILING")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "document_type": self.document_type,
                "period_of_report": self.period_of_report,
                "issuer_cik": self.issuer_cik, "issuer_name": self.issuer_name,
                "issuer_trading_symbol": self.issuer_trading_symbol,
                "owners": [owner.to_dict() for owner in self.owners],
                "transactions": [row.to_dict() for row in self.transactions],
                "footnote_ids": list(self.footnote_ids),
                "is_amendment": self.is_amendment,
                "public_observability_instant": None,
                "public_observability_state": self.public_observability_state,
                "violations": self.violations(), "detail": self.detail}


def _strip_namespace(root: ElementTree.Element) -> None:
    for element in root.iter():
        if "}" in element.tag:
            element.tag = element.tag.split("}", 1)[1]


def _transaction(node: ElementTree.Element, derivative: bool) -> Form4Transaction:
    security_title, _ = _value_of(node, "securityTitle")
    transaction_date, _ = _value_of(node, "transactionDate")
    coding = node.find("transactionCoding")
    code = _text(coding.find("transactionCode")) if coding is not None else None
    if code is None and coding is not None:
        code, _ = _value_of(coding, "transactionCode")
    amounts = node.find("transactionAmounts")
    shares_raw, _ = _value_of(amounts, "transactionShares")
    price_raw, price_footnote = _value_of(amounts, "transactionPricePerShare")
    acquired_raw, _ = _value_of(amounts, "transactionAcquiredDisposedCode")
    post = node.find("postTransactionAmounts")
    following_raw, _ = _value_of(post, "sharesOwnedFollowingTransaction")
    nature = node.find("ownershipNature")
    direct_raw, _ = _value_of(nature, "directOrIndirectOwnership")
    price = _number(price_raw)
    if price is not None:
        price_state = PRICE_PRESENT
    elif price_footnote:
        price_state = PRICE_IN_FOOTNOTE
    else:
        price_state = PRICE_ABSENT
    swap = _flag(coding, "equitySwapInvolved") if coding is not None else None
    return Form4Transaction(
        security_title=security_title, transaction_date=transaction_date,
        transaction_code=code, acquired_disposed=acquired_raw,
        shares=_number(shares_raw), price_per_share=price, price_state=price_state,
        shares_owned_following=_number(following_raw), direct_or_indirect=direct_raw,
        derivative=derivative, equity_swap_involved=swap)


def parse_form4_document(payload: bytes) -> Form4Facts:
    """Extract facts from one Form 4 XML document.

    Never raises on bad input: an unparseable document is a state, because a
    pipeline that crashes on one malformed filing loses the evidence that the
    filing was malformed.
    """
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as error:
        return Form4Facts(PARSE_MALFORMED_XML, detail=str(error))
    _strip_namespace(root)
    if root.tag != "ownershipDocument":
        return Form4Facts(PARSE_NOT_OWNERSHIP_DOCUMENT, detail=f"root tag {root.tag!r}")

    document_type = _text(root.find("documentType"))
    if document_type is None:
        return Form4Facts(PARSE_DOCUMENT_TYPE_UNREADABLE,
                          detail="documentType element absent or empty")
    normalised = document_type.strip().upper()
    if normalised not in ("4", "4/A"):
        return Form4Facts(PARSE_NOT_FORM_4, document_type=document_type,
                          detail=f"documentType {document_type!r} is not Form 4")

    issuer = root.find("issuer")
    owners: list[ReportingOwner] = []
    for owner_node in root.findall("reportingOwner"):
        identity = owner_node.find("reportingOwnerId")
        relationship = owner_node.find("reportingOwnerRelationship")
        owners.append(ReportingOwner(
            cik=_text(identity.find("rptOwnerCik")) if identity is not None else None,
            name=_text(identity.find("rptOwnerName")) if identity is not None else None,
            is_director=_flag(relationship, "isDirector"),
            is_officer=_flag(relationship, "isOfficer"),
            is_ten_percent_owner=_flag(relationship, "isTenPercentOwner"),
            is_other=_flag(relationship, "isOther"),
            officer_title=_text(relationship.find("officerTitle"))
            if relationship is not None else None))

    transactions: list[Form4Transaction] = []
    non_derivative = root.find("nonDerivativeTable")
    if non_derivative is not None:
        for node in non_derivative.findall("nonDerivativeTransaction"):
            transactions.append(_transaction(node, derivative=False))
    derivative = root.find("derivativeTable")
    if derivative is not None:
        for node in derivative.findall("derivativeTransaction"):
            transactions.append(_transaction(node, derivative=True))

    footnotes = root.find("footnotes")
    footnote_ids = tuple(node.get("id", "") for node in footnotes.findall("footnote")) \
        if footnotes is not None else ()

    return Form4Facts(
        PARSE_OK, document_type=document_type,
        period_of_report=_text(root.find("periodOfReport")),
        issuer_cik=_text(issuer.find("issuerCik")) if issuer is not None else None,
        issuer_name=_text(issuer.find("issuerName")) if issuer is not None else None,
        issuer_trading_symbol=_text(issuer.find("issuerTradingSymbol"))
        if issuer is not None else None,
        owners=tuple(owners), transactions=tuple(transactions),
        footnote_ids=footnote_ids, is_amendment=normalised == "4/A")
