from datetime import date, datetime, timedelta, timezone
import importlib.util
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "research" / "edge_search" / "treasury_auction_zf" / "harness.py"
spec = importlib.util.spec_from_file_location("treasury_auction_zf_harness", MODULE)
h = importlib.util.module_from_spec(spec)
assert spec.loader is not None
import sys
sys.modules[spec.name] = h
spec.loader.exec_module(h)


def row(**overrides):
    base = {
        "announcement_date": "2024-01-18",
        "auction_date": "2024-01-24",
        "security_type": "Note",
        "security_term": "5-Year",
        "reopening": "No",
        "competitive_close_et": "1:00 p.m. ET",
        "original_announcement_url": "https://www.treasurydirect.gov/instit/annceresult/press/preanre/2024/A_TEST.pdf",
        "cusip": "91282TEST",
    }
    base.update(overrides)
    return base


def test_dst_is_date_specific_not_fixed_utc():
    winter = h.normalize_treasury_row(row(auction_date="2024-01-24"))
    summer = h.normalize_treasury_row(row(announcement_date="2024-03-21", auction_date="2024-03-27"))
    assert winter.close_utc.hour == 18  # EST
    assert summer.close_utc.hour == 17  # EDT


def test_reopening_is_preserved_and_not_excluded():
    event = h.normalize_treasury_row(row(reopening="Yes"))
    assert event.reopening is True


def test_bad_or_ambiguous_timestamp_is_rejected():
    with pytest.raises(h.ProtocolError):
        h.normalize_treasury_row(row(competitive_close_et="1:00 pm"))
    with pytest.raises(h.ProtocolError):
        h.normalize_treasury_row(row(competitive_close_et="25:00 ET"))


def test_contract_roll_rule_is_outcome_blind_and_deterministic():
    # 14-day threshold retains March before the roll cutoff, then moves to June.
    assert h.select_zf_contract(date(2024, 2, 15)).symbol == "ZFH24"
    assert h.select_zf_contract(date(2024, 2, 16)).symbol == "ZFH24"
    assert h.select_zf_contract(date(2024, 2, 17)).symbol == "ZFM24"
    # Late-May 5Y auction is on the deferred Sep contract.
    assert h.select_zf_contract(date(2024, 5, 28)).symbol == "ZFU24"


def test_missing_bbo_blocks_event_instead_of_using_mid_or_stale_quote():
    event = h.normalize_treasury_row(row())
    with pytest.raises(h.MissingBBO):
        h.calculate_event(event, [])


def test_no_lookahead_pre_exit_must_be_strictly_before_auction_close():
    event = h.normalize_treasury_row(row())
    t = event.close_utc
    quotes = [
        h.BBO(event.pre_entry_utc, 110.0, 110.01),
        h.BBO(t, 109.98, 109.99),  # quote exactly at T is forbidden for PRE exit
        h.BBO(event.post_entry_utc, 109.99, 110.00),
        h.BBO(event.post_exit_utc, 110.01, 110.02),
    ]
    with pytest.raises(h.MissingBBO):
        h.calculate_event(event, quotes)


def test_pre_short_and_post_long_arithmetic_uses_executable_sides_and_fees():
    event = h.normalize_treasury_row(row())
    t = event.close_utc
    quotes = [
        h.BBO(event.pre_entry_utc, 110.000000, 110.0078125),
        h.BBO(t - timedelta(seconds=1), 109.9765625, 109.9843750),
        h.BBO(event.post_entry_utc, 109.9843750, 109.9921875),
        h.BBO(event.post_exit_utc, 110.0156250, 110.0234375),
    ]
    result = h.calculate_event(event, quotes)
    assert result.pre.entry_price == pytest.approx(110.0)       # sell bid
    assert result.pre.exit_price == pytest.approx(109.984375)   # buy ask
    assert result.pre.gross_usd == pytest.approx(15.625)
    assert result.pre.net_usd == pytest.approx(9.625)            # minus $6 round trip
    assert result.post.entry_price == pytest.approx(109.9921875) # buy ask
    assert result.post.exit_price == pytest.approx(110.015625)   # sell bid
    assert result.post.gross_usd == pytest.approx(23.4375)
    assert result.post.net_usd == pytest.approx(17.4375)


def test_announcement_must_precede_pre_entry_no_lookahead():
    with pytest.raises(h.ProtocolError):
        h.normalize_treasury_row(row(announcement_date="2024-01-24"))


def test_manifest_is_deterministic_and_digest_stable():
    a = h.normalize_treasury_row(row())
    b = h.normalize_treasury_row(row(announcement_date="2024-02-15", auction_date="2024-02-21", cusip="91282TES2"))
    m1 = h.build_event_manifest([row(announcement_date="2024-02-15", auction_date="2024-02-21", cusip="91282TES2"), row()])
    m2 = h.build_event_manifest([row(), row(announcement_date="2024-02-15", auction_date="2024-02-21", cusip="91282TES2")])
    assert [e.auction_date for e in m1] == [a.auction_date, b.auction_date]
    assert h.manifest_digest(m1) == h.manifest_digest(m2)
