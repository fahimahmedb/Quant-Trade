"""PIT corporate-action clocks and finite contractual quantities."""

import pytest

from quant.dataplane.corporate_actions import CorporateActionBook, CorporateActionEvent, CorporateActionLeg


H = ("sha256:" + "a" * 64,)


@pytest.mark.parametrize("number", [float("nan"), float("inf"), True])
@pytest.mark.parametrize("kind", ["CASH", "STOCK", "SPIN", "SPLIT"])
def test_nonfinite_and_boolean_terms_cannot_be_positive_consideration(number, kind):
    with pytest.raises(ValueError):
        if kind == "SPLIT":
            CorporateActionEvent("fixture", "SPLIT", "2026-10-20", "2026-10-21", H,
                                 source_security_id="fixture", split_ratio=number)
        elif kind == "CASH":
            CorporateActionLeg(kind, cash_per_source_share=number, currency="USD")
        else:
            CorporateActionLeg(kind, target_security_id="fixture", units_per_source_share=number)


def event(identity, knowledge, effective):
    return CorporateActionEvent(identity, "SPLIT", knowledge, effective, H,
                                source_security_id="fixture", split_ratio=2)


def test_known_and_effective_order_follow_utc_instants():
    earlier = event("earlier", "2026-10-20T13:00:00+02:00", "2026-10-21T13:00:00+02:00")
    later = event("later", "2026-10-20T12:00:00Z", "2026-10-21T12:00:00Z")
    book = CorporateActionBook([later, earlier])
    assert [e.event_id for e in book.known_as_of("2026-10-22")] == ["earlier", "later"]
    assert [e.event_id for e in book.effective_as_of("2026-10-22")] == ["earlier", "later"]


def test_equal_instants_use_stable_identity_tie_breaker():
    first = event("a", "2026-10-20T14:00:00+02:00", "2026-10-21T14:00:00+02:00")
    second = event("b", "2026-10-20T12:00:00Z", "2026-10-21T12:00:00Z")
    for entries in ([first, second], [second, first]):
        book = CorporateActionBook(entries)
        assert [e.event_id for e in book.known_as_of("2026-10-22")] == ["a", "b"]
        assert [e.event_id for e in book.effective_as_of("2026-10-22")] == ["a", "b"]


def test_exact_knowledge_and_effective_boundaries_do_not_expose_later_revisions():
    initial = event("initial", "2026-10-20T12:00:00Z", "2026-10-21T12:00:00Z")
    revision = event("revision", "2026-10-22T12:00:00Z", "2026-10-21T12:00:00Z")
    book = CorporateActionBook([revision, initial])
    assert book.known_as_of("2026-10-20T11:59:59.999999Z") == ()
    assert book.known_as_of("2026-10-20T12:00:00Z") == (initial,)
    assert book.effective_as_of("2026-10-21T11:59:59.999999Z") == ()
    assert book.effective_as_of("2026-10-21T12:00:00Z") == (initial,)
    assert book.known_as_of("2026-10-22T12:00:00Z") == (initial, revision)
