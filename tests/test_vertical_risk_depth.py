"""Fail-closed numerical admission through every existing RISK entrypoint."""

from dataclasses import fields, replace
from unittest.mock import patch

import pytest

from quant.book.ledger import Ledger
from quant.desk.risk import RiskLimits, assess, evaluate, project, verify_final


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), True])
@pytest.mark.parametrize("entrypoint", [evaluate, verify_final, project])
def test_invalid_target_cannot_disappear_during_projection(tmp_path, value, entrypoint):
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    args = (book, "fixture", {"SYNTH": value})
    with pytest.raises(ValueError):
        entrypoint(*args, **({} if entrypoint is project else {"limits": RiskLimits()}))


@pytest.mark.parametrize("field", [item.name for item in fields(RiskLimits)])
def test_nonfinite_limit_cannot_disable_a_comparison(tmp_path, field):
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    limits = replace(RiskLimits(), **{field: float("nan")})
    with pytest.raises(ValueError):
        evaluate(book, "fixture", {"SYNTH": 90}, limits)


@pytest.mark.parametrize("field", ["nav", "drawdown", "initial_capital", "portfolio"])
def test_direct_assess_does_not_pass_nonfinite_accounting(field):
    args = dict(portfolio={}, nav=100, drawdown=0, limits=RiskLimits(), initial_capital=100)
    args[field] = {"SYNTH": float("nan")} if field == "portfolio" else float("nan")
    with pytest.raises(ValueError):
        assess(**args)


def test_corrupt_sleeve_cannot_be_filtered_out_by_symbol_projection(tmp_path):
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    book.apply_fill("SYNTH", 1, 10, 0, "2026-10-20", "fixture", "one")
    book.sleeves["fixture"]["SYNTH"].quantity = float("nan")
    with pytest.raises(ValueError):
        evaluate(book, "fixture", {}, RiskLimits(), prices={"SYNTH": 10})


def test_invalid_valuation_vector_and_final_cash_adjustment_block(tmp_path):
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    with pytest.raises(ValueError):
        evaluate(book, "fixture", {}, RiskLimits(), prices={"SYNTH": float("nan")})
    with pytest.raises(ValueError):
        verify_final(book, "fixture", {}, RiskLimits(), nav_adjustment=float("nan"))


def test_no_nan_verdict_can_reach_a_book_mutation(tmp_path):
    book = Ledger(tmp_path / "book.json", authority="EVALUATION", initial_capital=100)
    with patch.object(book, "apply_fill", side_effect=AssertionError("must not book")):
        with pytest.raises(ValueError):
            evaluate(book, "fixture", {"SYNTH": float("nan")}, RiskLimits())
    assert book.state.fills == 0
