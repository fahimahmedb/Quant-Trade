"""Futures excess-return panel built from a pinned pysystemtrade data snapshot.

Why a derived index rather than raw prices
-------------------------------------------
Back-adjusted futures prices are a *difference* series: they can be negative
and their level is not the notional of any contract. The Book values a position
as ``quantity * price`` and research measures ``price(t+1)/price(t) - 1``, so
feeding it back-adjusted levels would make notional, gross exposure and returns
all wrong. Instead each instrument becomes a fully collateralised excess-return
index:

``r_t = (A_t - A_{t-1}) / P_{t-1} - roll_cost_t``    ``X_t = X_{t-1} * (1 + r_t)``

where ``A`` is the back-adjusted price (so the P&L across a roll is the P&L of
the contract actually held), ``P`` is the price of the contract held and
``roll_cost`` charges two half-spreads plus two commissions whenever the held
contract changes. ``X`` is positive, its percentage move is the economic return
per unit of notional, and ``quantity * X`` is the notional exposure — which is
exactly what the existing Book, RISK and research code already assume.

The excess return excludes the collateral yield, so strategy returns over this
panel are returns in excess of cash. That is the hurdle the Research Factory
must clear, and it is why no separate risk-free hurdle is added on top.

Point-in-time contract
----------------------
* A bar dated ``t`` uses only the daily close snapshot of ``t`` (the last
  intraday snapshot recorded for that calendar date in the source files).
* ``carry_ann`` is the annualised carry implied by the held and the adjacent
  contract on ``t``: ``(P - C) / P / years(C_contract - P_contract)``; empty
  when either leg was not observed.
* A market that did not trade on a session in the shared calendar carries its
  previous index level forward (no price change occurred) for at most
  ``MAX_STALE_SESSIONS`` sessions and is flagged ``stale=1``. It is never
  interpolated.
* ``volume`` is unavailable in the source and is written as ``0``. Capacity is
  therefore **not modelled** from this panel; this is a declared caveat.

Only the standard library is used, like the rest of the product.
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path
from typing import Any

from .panel import PricePanel


FUTURES_DATASET = "futures_excess_return_daily"

#: Liquid, diversified contracts with history from 2002 or earlier, so the
#: aligned panel has one common start and no instrument enters mid-sample
#: (entry mid-sample would be a selection decision taken with hindsight).
FUTURES_UNIVERSE = [
    # equity indices
    "SP500", "NASDAQ", "DAX", "FTSE100", "HANG",
    # government bonds
    "US2", "US5", "US10", "US20", "GILT", "JGB",
    # currencies (vs USD)
    "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "MXP",
    # energy
    "CRUDE_W", "GAS_US", "HEATOIL",
    # metals
    "GOLD", "SILVER", "COPPER", "PLAT",
    # agriculture / livestock
    "CORN", "WHEAT", "SOYBEAN", "SUGAR11", "LIVECOW", "LEANHOG",
]
FUTURES_BENCHMARK = "SP500"
DEFAULT_START = "2002-01-01"
MAX_STALE_SESSIONS = 5
#: A session enters the shared calendar only when most markets traded on it,
#: so one exchange's local holiday does not create a session for everyone.
CALENDAR_QUORUM = 0.5

SOURCE_REPOSITORY = "https://github.com/pst-group/pysystemtrade"


def _daily_last(path: Path, columns: list[str]) -> dict[str, dict[str, str]]:
    """Last intraday snapshot per calendar date, keyed by ISO date."""
    out: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            stamp = row["DATETIME"]
            day = stamp[:10]
            out[day] = {name: row.get(name, "") for name in columns}
    return out


def _months(contract: str) -> int:
    value = int(float(contract)) // 100          # YYYYMMDD -> YYYYMM
    return (value // 100) * 12 + value % 100


def _config(root: Path) -> tuple[dict[str, dict[str, str]], dict[str, float]]:
    with (root / "csvconfig" / "instrumentconfig.csv").open(encoding="utf-8") as handle:
        instruments = {row["Instrument"]: row for row in csv.DictReader(handle)}
    with (root / "csvconfig" / "spreadcosts.csv").open(encoding="utf-8") as handle:
        spreads = {row["Instrument"]: float(row["SpreadCost"]) for row in csv.DictReader(handle)}
    return instruments, spreads


def source_commit(checkout: Path) -> str | None:
    """The exact source revision, so the derived bytes can be re-derived."""
    try:
        return subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _file_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return "sha256:" + digest.hexdigest()


def build_futures_panel(checkout: Path, universe: list[str] | None = None,
                        start: str = DEFAULT_START) -> tuple[PricePanel, dict[str, Any]]:
    """Derive the excess-return panel from a pysystemtrade checkout.

    ``checkout`` is the repository root (the directory containing ``data/``).
    """
    universe = list(universe or FUTURES_UNIVERSE)
    root = checkout / "data" / "futures"
    instruments, spreads = _config(root)
    inputs: list[Path] = [root / "csvconfig" / "instrumentconfig.csv",
                          root / "csvconfig" / "spreadcosts.csv"]
    series: dict[str, dict[str, dict[str, Any]]] = {}
    for symbol in universe:
        adjusted_path = root / "adjusted_prices_csv" / f"{symbol}.csv"
        multiple_path = root / "multiple_prices_csv" / f"{symbol}.csv"
        inputs += [adjusted_path, multiple_path]
        adjusted = _daily_last(adjusted_path, ["price"])
        multiple = _daily_last(multiple_path, ["PRICE", "PRICE_CONTRACT", "CARRY",
                                               "CARRY_CONTRACT"])
        config = instruments[symbol]
        point_size = float(config["Pointsize"])
        per_block = float(config["PerBlock"] or 0.0)
        spread = spreads.get(symbol, 0.0)
        level, previous = 100.0, None
        rows: dict[str, dict[str, Any]] = {}
        for day in sorted(set(adjusted) & set(multiple)):
            held = multiple[day]
            if not adjusted[day]["price"] or not held["PRICE"] or not held["PRICE_CONTRACT"]:
                continue
            a_now, p_now = float(adjusted[day]["price"]), float(held["PRICE"])
            contract = held["PRICE_CONTRACT"]
            roll = 0
            if previous is not None and p_now > 0 and previous["price"] > 0:
                ret = (a_now - previous["adjusted"]) / previous["price"]
                if contract != previous["contract"]:
                    roll = 1
                    # close the old contract and open the new one
                    ret -= 2.0 * spread / previous["price"]
                    ret -= 2.0 * per_block / (point_size * previous["price"])
                level *= 1.0 + ret
            carry = None
            if held["CARRY"] and held["CARRY_CONTRACT"] and p_now > 0:
                years = (_months(held["CARRY_CONTRACT"]) - _months(contract)) / 12.0
                if years != 0:
                    carry = (p_now - float(held["CARRY"])) / p_now / years
            previous = {"adjusted": a_now, "price": p_now, "contract": contract}
            if day >= start:
                rows[day] = {"level": level, "carry": carry, "roll": roll}
        series[symbol] = rows

    counts: dict[str, int] = {}
    for rows in series.values():
        for day in rows:
            counts[day] = counts.get(day, 0) + 1
    calendar = sorted(day for day, count in counts.items()
                      if count >= CALENDAR_QUORUM * len(universe))

    panel_rows: list[dict[str, Any]] = []
    stale_bars = 0
    for symbol, rows in series.items():
        last: dict[str, Any] | None = None
        stale = 0
        for day in calendar:
            if day in rows:
                last, stale = rows[day], 0
                observed = True
            elif last is not None and stale < MAX_STALE_SESSIONS:
                stale += 1
                observed = False
            else:
                continue
            level = last["level"]
            row = {"date": day, "symbol": symbol, "open": level, "high": level, "low": level,
                   "close": level, "adj_close": level, "volume": 0.0,
                   "stale": 0.0 if observed else 1.0,
                   "roll": float(last["roll"]) if observed else 0.0}
            if observed and last["carry"] is not None:
                row["carry_ann"] = last["carry"]
            if not observed:
                stale_bars += 1
            panel_rows.append(row)
    panel = PricePanel(panel_rows)
    commit = source_commit(checkout)
    provenance = {
        "source": f"{SOURCE_REPOSITORY} data/futures (adjusted_prices_csv, "
                  f"multiple_prices_csv, csvconfig) @ {commit or 'unknown commit'}",
        "source_commit": commit,
        "source_input_digest": _file_digest(inputs),
        "timestamp_semantics": "last intraday snapshot recorded for the calendar date in "
                               "the source files; treated as that session's close",
        "derivation": "excess-return index per instrument: back-adjusted daily change "
                      "divided by the held contract's previous price, minus two "
                      "half-spreads and two commissions on each roll (see "
                      "quant.dataplane.futures)",
        "stale_bars_carried_forward": stale_bars,
        "caveats": [
            "third-party research data (pysystemtrade repository), not an exchange "
            "feed; not independently verified against exchange settlements",
            "universe is today's liquid contract list: instruments that were delisted "
            "before the snapshot are absent (mild survivorship)",
            "returns are in each contract's local currency; P&L currency translation "
            "(second order for a margined futures position) is not modelled",
            "volume is unavailable and written as 0: execution capacity is NOT modelled",
            "index excludes collateral interest: every return is an excess return over "
            "cash",
            "roll costs use the repository's current spread and commission estimates "
            "for the whole history, which likely understates early-2000s costs",
            f"a market closed on a shared session carries its last level forward for at "
            f"most {MAX_STALE_SESSIONS} sessions and is flagged stale=1",
        ],
    }
    return panel, provenance


#: The exact snapshot the committed panel was derived from.
PINNED_COMMIT = "8958c49c38b1e4a8c07f0e4375d5e9cb68a087f7"


def fetch_source(destination: Path, commit: str = PINNED_COMMIT) -> Path:
    """Materialise the pinned source through git (the only egress this
    environment allows), fetching only the futures data directories."""
    destination.mkdir(parents=True, exist_ok=True)
    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(destination), *args], check=True,
                       capture_output=True, text=True)
    if not (destination / ".git").exists():
        git("init", "-q")
        git("remote", "add", "origin", SOURCE_REPOSITORY + ".git")
    git("sparse-checkout", "set", "data/futures/adjusted_prices_csv",
        "data/futures/multiple_prices_csv", "data/futures/csvconfig")
    git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit)
    git("checkout", "-q", commit)
    return destination
