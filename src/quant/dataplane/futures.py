"""Futures excess-return panel built from a pinned pysystemtrade data snapshot.

Why a derived index rather than raw prices
-------------------------------------------
Back-adjusted futures prices are a *difference* series: they can be negative
and their level is not the notional of any contract. The Book values a position
as ``quantity * price`` and research measures ``price(t+1)/price(t) - 1``, so
feeding it back-adjusted levels would make notional, gross exposure and returns
all wrong. Instead each instrument becomes a fully collateralised excess-return
index:

``r_t = (A_t - A_{t-1}) / P_{t-1}``    ``X_t = X_{t-1} * (1 + r_t)``

where ``A`` is the back-adjusted price (so the P&L across a roll is the P&L of
the contract actually held) and ``P`` is the price of the contract held. ``X``
is positive, its percentage move is the economic return per unit of notional,
and ``quantity * X`` is the notional exposure — which is exactly what the
existing Book, RISK and research code already assume.

Roll costs are *not* inside ``X``: a cost subtracted from an index is credited
to every short position (red-team finding). They are published as the
``roll_cost`` feature (two half-spreads plus two commissions, as a fraction of
notional, on the session the held contract changed) and charged on the
absolute position by research (``walk_forward``) and by the Desk.

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
FUTURES_BROAD_DATASET = "futures_excess_return_daily_broad"
BROAD_START = "1990-01-01"
#: Declared before any broad-panel result was seen: the asset classes a
#: diversified trend/carry programme trades, excluding volatility futures
#: (structurally short-volatility carry), single stocks, sector/housing/weather
#: and index-of-indices contracts.
BROAD_ASSET_CLASSES = frozenset({"Equity", "Bond", "FX", "OilGas", "Metals", "Ags"})
#: Same exposure in a different contract size would double-count one market.
DUPLICATE_MARKERS = ("micro", "mini", "small", "_e-")
BROAD_MIN_YEARS = 3.0
#: Only contracts still quoted at the snapshot are available (survivorship,
#: declared as a caveat); this is the date that defines "still quoted".
BROAD_LIVE_AFTER = "2024-01-01"
#: Data-quality rule: a move beyond this size that is undone (to within 25%)
#: inside ``GLITCH_WINDOW`` observations is a price-scale error in the source,
#: not a market event. The instrument is excluded, never "repaired".
GLITCH_MOVE = 0.8
GLITCH_WINDOW = 5
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


def select_broad_universe(checkout: Path, start: str = BROAD_START) -> list[str]:
    """Mechanical, pre-declared selection rule for the broad panel."""
    import datetime as dt
    root = checkout / "data" / "futures"
    instruments, spreads = _config(root)
    chosen = []
    for path in sorted((root / "adjusted_prices_csv").glob("*.csv")):
        symbol = path.stem
        if any(marker in symbol.lower() for marker in DUPLICATE_MARKERS):
            continue
        config = instruments.get(symbol)
        if (config is None or symbol not in spreads
                or config["AssetClass"] not in BROAD_ASSET_CLASSES
                or not (root / "multiple_prices_csv" / f"{symbol}.csv").exists()):
            continue
        with path.open(encoding="utf-8") as handle:
            stamps = [row["DATETIME"][:10] for row in csv.DictReader(handle)]
        if not stamps or stamps[-1] < BROAD_LIVE_AFTER:
            continue
        first = max(stamps[0], start)
        years = (dt.date.fromisoformat(stamps[-1]) - dt.date.fromisoformat(first)).days / 365.25
        if years >= BROAD_MIN_YEARS:
            chosen.append(symbol)
    return chosen


def _scale_glitches(rows: dict[str, dict[str, Any]]) -> list[str]:
    days = sorted(rows)
    levels = [rows[day]["level"] for day in days]
    found = []
    for index in range(1, len(levels)):
        move = levels[index] / levels[index - 1] - 1.0
        if abs(move) < GLITCH_MOVE:
            continue
        for later in range(index + 1, min(index + 1 + GLITCH_WINDOW, len(levels))):
            if 0.8 <= levels[later] / levels[index - 1] <= 1.25:
                found.append(days[index])
                break
    return found


def build_futures_panel(checkout: Path, universe: list[str] | None = None,
                        start: str = DEFAULT_START,
                        calendar_symbol: str | None = None,
                        cost_feature: bool = False) -> tuple[PricePanel, dict[str, Any]]:
    """Derive the excess-return panel from a pysystemtrade checkout.

    ``checkout`` is the repository root (the directory containing ``data/``).
    With ``calendar_symbol`` the sessions are that contract's trading days and
    every other contract enters at its own first observation (staggered);
    without it, a session needs a quorum of the universe.
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
            roll_cost = 0.0
            if previous is not None and p_now > 0 and previous["price"] > 0:
                ret = (a_now - previous["adjusted"]) / previous["price"]
                if contract != previous["contract"]:
                    # close the old contract and open the new one
                    roll_cost = (2.0 * spread / previous["price"]
                                 + 2.0 * per_block / (point_size * previous["price"]))
                level *= 1.0 + ret
            carry = None
            if held["CARRY"] and held["CARRY_CONTRACT"] and p_now > 0:
                years = (_months(held["CARRY_CONTRACT"]) - _months(contract)) / 12.0
                if years != 0:
                    carry = (p_now - float(held["CARRY"])) / p_now / years
            previous = {"adjusted": a_now, "price": p_now, "contract": contract}
            if day >= start:
                # one-way cost of trading one unit of notional today: half-spread
                # plus commission, both at the repository's current estimates
                cost = ((spread + per_block / point_size) / p_now * 10_000.0
                        if p_now > 0 else None)
                rows[day] = {"level": level, "carry": carry, "roll_cost": roll_cost,
                             "cost": cost}
        series[symbol] = rows

    excluded: dict[str, list[str]] = {}
    for symbol in list(series):
        glitches = _scale_glitches(series[symbol])
        if glitches:
            excluded[symbol] = glitches
            del series[symbol]
    universe = [symbol for symbol in universe if symbol in series]
    import datetime as _dt

    def weekday(day: str) -> bool:
        # Globex Sunday-evening snapshots are not sessions (red-team finding).
        return _dt.date.fromisoformat(day).weekday() < 5

    if calendar_symbol:
        calendar = sorted(day for day in series[calendar_symbol] if weekday(day))
    else:
        counts: dict[str, int] = {}
        for rows in series.values():
            for day in rows:
                counts[day] = counts.get(day, 0) + 1
        calendar = sorted(day for day, count in counts.items()
                          if count >= CALENDAR_QUORUM * len(universe) and weekday(day))

    panel_rows: list[dict[str, Any]] = []
    stale_bars = 0
    for symbol, rows in series.items():
        last: dict[str, Any] | None = None
        stale = 0
        observed_days = sorted(rows)
        cursor = 0
        pending_roll = 0.0
        for day in calendar:
            # A roll on a day that is not a session (weekend, the reference
            # market's holiday) is charged on the next session, never dropped.
            while cursor < len(observed_days) and observed_days[cursor] < day:
                pending_roll += rows[observed_days[cursor]]["roll_cost"]
                cursor += 1
            if day in rows:
                last, stale = rows[day], 0
                observed = True
                pending_roll += rows[day]["roll_cost"]
                cursor += 1
            elif last is not None and stale < MAX_STALE_SESSIONS:
                stale += 1
                observed = False
            else:
                continue
            level = last["level"]
            row = {"date": day, "symbol": symbol, "open": level, "high": level, "low": level,
                   "close": level, "adj_close": level, "volume": 0.0,
                   "stale": 0.0 if observed else 1.0}
            if observed and pending_roll > 0:
                row["roll_cost"] = pending_roll
                pending_roll = 0.0
            if observed and last["carry"] is not None:
                row["carry_ann"] = last["carry"]
            if cost_feature and last.get("cost") is not None:
                row["cost_bps"] = last["cost"]
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
                      "divided by the held contract's previous price; roll costs (two "
                      "half-spreads and two commissions) published as the roll_cost "
                      "feature and charged on absolute positions downstream; cost_bps "
                      "is the one-way half-spread plus commission at that day's price "
                      "(see quant.dataplane.futures)",
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
        ] + ([f"sessions are the trading days of {calendar_symbol}; a contract trading on "
              f"a day {calendar_symbol} did not trade accrues that move to the next "
              f"session (no return is lost, it is re-timed)",
              "staggered universe: each contract enters at its first observation"]
             if calendar_symbol else []),
        "calendar_symbol": calendar_symbol,
        "universe": universe,
        "excluded_for_data_quality": excluded,
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
