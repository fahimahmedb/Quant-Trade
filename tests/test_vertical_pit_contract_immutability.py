"""CP043: JSON list inputs must not mutate already admitted frozen PIT facts."""
from dataclasses import asdict
import json

import pytest

from quant.dataplane.corporate_actions import CorporateActionBook, CorporateActionEvent, CorporateActionLeg
from quant.dataplane.identity import (
    IdentityBook, IssuerIdentity, IssuerNameInterval, ListingInterval,
    SecurityIdentity, TickerInterval,
)


KINDS = ['issuer', 'security', 'name', 'ticker', 'listing', 'action']


def construct(kind, lineage):
    if kind == 'issuer':
        return IssuerIdentity('I-SYN', '2026-01-01', None, {'lei': 'SYNTHETIC'}, lineage)
    if kind == 'security':
        return SecurityIdentity('S-SYN', 'I-SYN', 'EQUITY', '2026-01-01', None, {}, lineage)
    if kind == 'name':
        return IssuerNameInterval('I-SYN', 'Synthetic issuer', '2026-01-01', None, lineage)
    if kind == 'ticker':
        return TickerInterval('S-SYN', 'SYN', '2026-01-01', None, lineage, venue='XNYS')
    if kind == 'listing':
        return ListingInterval('S-SYN', 'XNYS', '2026-01-01', None, lineage)
    return CorporateActionEvent('EVENT-SYN', 'MERGER', '2026-01-02', '2026-01-03', lineage,
                                source_security_id='S-SYN',
                                legs=(CorporateActionLeg('CASH', cash_per_source_share=1, currency='USD'),))


def identity_fixture():
    lineages = {name: ['sha256:' + letter*64]
                for name, letter in zip(KINDS[:5], 'abcde')}
    records = {name: construct(name, hashes) for name, hashes in lineages.items()}
    book = IdentityBook(issuers=[records['issuer']], securities=[records['security']],
                        names=[records['name']], tickers=[records['ticker']], listings=[records['listing']])
    return book, lineages


@pytest.mark.parametrize('kind', KINDS[:5])
@pytest.mark.parametrize('mutation', ['clear', 'inject_unvalidated_hash'])
def test_caller_lineage_list_cannot_change_admitted_pit_resolution(kind, mutation):
    book, lineages = identity_fixture()
    expected_ticker = book.resolve_ticker('SYN', as_of='2026-02-01', venue='XNYS')
    expected_name = book.resolve_name('I-SYN', '2026-02-01')
    if mutation == 'clear':
        lineages[kind].clear()
    else:
        lineages[kind].append('unvalidated-after-construction')
    assert book.resolve_ticker('SYN', as_of='2026-02-01', venue='XNYS') == expected_ticker
    assert book.resolve_name('I-SYN', '2026-02-01') == expected_name


@pytest.mark.parametrize('mutation', ['clear_legs', 'append_forbidden_spin', 'clear_lineage', 'append_bad_lineage'])
def test_mutating_source_arrays_cannot_change_frozen_corporate_action(mutation):
    lineage = ['sha256:' + 'f'*64]
    legs = [CorporateActionLeg('CASH', cash_per_source_share=1, currency='USD')]
    action = CorporateActionEvent('EVENT-SYN', 'MERGER', '2026-01-02', '2026-01-03', lineage,
                                  source_security_id='S-SYN', legs=legs)
    book = CorporateActionBook([action])
    expected_legs = tuple(action.legs)
    expected_lineage = book.lineage_hashes()
    if mutation == 'clear_legs':
        legs.clear()
    elif mutation == 'append_forbidden_spin':
        legs.append(CorporateActionLeg('SPIN', target_security_id='S-FOREIGN', units_per_source_share=1))
    elif mutation == 'clear_lineage':
        lineage.clear()
    else:
        lineage.append('not-a-qualified-evidence-hash')
    assert tuple(action.legs) == expected_legs
    assert book.lineage_hashes() == expected_lineage
    assert book.events_for_security('S-SYN', known_as_of='2026-01-04') == (action,)
    assert action.action_type == 'MERGER' and all(leg.kind != 'SPIN' for leg in action.legs)


@pytest.mark.parametrize('kind', KINDS)
def test_wire_reconstruction_preserves_contract_identity(kind):
    original = construct(kind, ('sha256:' + 'a'*64,))
    wire = json.loads(json.dumps(asdict(original), sort_keys=True))
    if kind == 'action':
        wire['legs'] = [CorporateActionLeg(**v) for v in wire['legs']]
    restored = type(original)(**wire)
    assert restored == original
    assert json.dumps(asdict(restored), sort_keys=True) == json.dumps(asdict(original), sort_keys=True)


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.parametrize('lineage', [[], ['not-a-sha256-evidence-hash']])
def test_invalid_lineage_is_still_refused_at_original_admission(kind, lineage):
    with pytest.raises(ValueError):
        construct(kind, lineage)


def test_knowledge_boundaries_and_resolved_lineage_keep_existing_semantics():
    book, _ = identity_fixture()
    assert book.resolve_ticker('SYN', as_of='2025-12-31', venue='XNYS').status == 'NOT_FOUND'
    result = book.resolve_ticker('SYN', as_of='2026-01-01', venue='XNYS')
    assert result.status == 'RESOLVED' and result.security_id == 'S-SYN'
    assert len(result.lineage_hashes) == 4
    assert book.resolve_name('I-SYN', '2026-01-01').name == 'Synthetic issuer'


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.parametrize('container', ['mapping', 'set'])
def test_lineage_container_cannot_silently_drop_metadata_or_order(kind, container):
    digest = 'sha256:' + 'a'*64
    malformed = {digest: {'unvalidated': 'silently ignored metadata'}} if container == 'mapping' else {digest}
    with pytest.raises(ValueError, match='lineage.*sequence|evidence.*sequence'):
        construct(kind, malformed)


@pytest.mark.parametrize('container', ['mapping', 'set'])
def test_consideration_container_cannot_be_silently_reinterpreted_as_leg_sequence(container):
    leg = CorporateActionLeg('CASH', cash_per_source_share=1, currency='USD')
    malformed = {leg: 'ignored quantity'} if container == 'mapping' else {leg}
    with pytest.raises(ValueError, match='legs.*sequence'):
        CorporateActionEvent('EVENT-SYN', 'MERGER', '2026-01-02', '2026-01-03',
                             ('sha256:' + 'a'*64,), source_security_id='S-SYN', legs=malformed)
