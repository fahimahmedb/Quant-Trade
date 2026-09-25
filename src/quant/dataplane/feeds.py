"""Apply collected feeds (``data/feeds``) to the committed datasets as forward bars.

The feeds are produced outside the sandbox (``scripts/fetch_feeds.py``, run by
the ``data-feeds`` GitHub Actions workflow) and reach this repository through
git. Applying them only ever **appends sessions after a dataset's last date**:
history inside a frozen research cohort is never rewritten, so the Control
Plane treats the result as forward evidence (and the ``pristine_after`` gate
lets the lifecycle act on it).

Adjusted prices: Yahoo restates ``adj_close`` retroactively at every dividend.
A forward bar is therefore rebased so that the feed's own adjusted series,
taken in its latest basis, joins the committed series at the seam date: daily
returns are preserved exactly and the committed history is untouched.
"""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

from .adapters import DataUnavailable
from .panel import PricePanel

FEEDS_BRANCH = "claude/data-feeds-6vr22g"


def read_latest(path: Path) -> dict[str, dict[str, Any]]:
    """Latest version of every key in an append-only stream (restatements win)."""
    latest: dict[str, tuple[str, dict[str, Any]]] = {}
    if not path.exists():
        return {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        base = item["key"].split("#restated@")[0]
        stamp = item.get("observed_at", "")
        if base not in latest or stamp >= latest[base][0]:
            latest[base] = (stamp, item["record"])
    return {key: record for key, (_, record) in latest.items()}


def checkout_feeds(repo: Path, destination: Path, branch: str = FEEDS_BRANCH) -> Path:
    """Materialise ``data/feeds`` from the data branch (git is the only egress)."""
    try:
        subprocess.run(["git", "-C", str(repo), "fetch", "-q", "origin", branch], check=True,
                       capture_output=True, text=True)
        listing = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only",
                                  "FETCH_HEAD", "data/feeds"], check=True,
                                 capture_output=True, text=True).stdout.split()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DataUnavailable(f"feeds branch {branch} unavailable: {exc}") from exc
    for name in listing:
        blob = subprocess.run(["git", "-C", str(repo), "show", f"FETCH_HEAD:{name}"],
                              check=True, capture_output=True).stdout
        target = destination / Path(name).relative_to("data/feeds")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    return destination


# --- ETF / equity daily bars -----------------------------------------------------
def etf_forward_rows(committed: PricePanel, feed: dict[str, dict[str, Any]],
                     symbols: Iterable[str]) -> list[dict[str, Any]]:
    """New complete sessions for ``symbols``, rebased at the seam date.

    A session is appended only when every symbol has a bar that day (the
    panel's aligned-date contract), and only if the feed also holds the seam
    date for every symbol; otherwise nothing is appended (a gap is never
    bridged by assumption).
    """
    symbols = list(symbols)
    last = max(committed.dates_for(symbols[0])) if committed.dates_for(symbols[0]) else None
    if last is None:
        return []
    by_symbol: dict[str, dict[str, dict[str, Any]]] = {}
    for record in feed.values():
        if record.get("symbol") in symbols:
            by_symbol.setdefault(record["symbol"], {})[record["date"]] = record
    factors = {}
    for symbol in symbols:
        seam = by_symbol.get(symbol, {}).get(last)
        if seam is None or not committed.has(last, symbol) or seam["adj_close"] <= 0:
            return []
        factors[symbol] = committed.price(last, symbol) / seam["adj_close"]
    new_dates = sorted({day for bars in by_symbol.values() for day in bars if day > last})
    rows = []
    for day in new_dates:
        if not all(day in by_symbol.get(symbol, {}) for symbol in symbols):
            break                       # stop at the first incomplete session
        for symbol in symbols:
            bar = by_symbol[symbol][day]
            rows.append({"date": day, "symbol": symbol, "open": bar["open"],
                         "high": bar["high"], "low": bar["low"], "close": bar["close"],
                         "adj_close": bar["adj_close"] * factors[symbol],
                         "volume": bar["volume"]})
    return rows


def extend_panel(committed: PricePanel, rows: list[dict[str, Any]]) -> PricePanel:
    existing = [{"date": day, "symbol": symbol, **bar,
                 **committed.features.get((day, symbol), {})}
                for (day, symbol), bar in committed.bars.items()]
    return PricePanel(existing + rows)


# --- FOMC schedule -----------------------------------------------------------------
def merged_fomc_days(committed: list[str], feed: dict[str, dict[str, Any]]) -> list[str]:
    """Add newly published decision days; refuse if the feed contradicts history."""
    live = sorted(record["decision_date"] for record in feed.values())
    if not live:
        return committed
    overlap_start, overlap_end = live[0], committed[-1] if committed else live[0]
    known = {day for day in committed if overlap_start <= day <= overlap_end}
    seen = {day for day in live if day <= overlap_end}
    if known != seen:
        raise DataUnavailable(f"FOMC feed contradicts the committed schedule: "
                              f"missing {sorted(known - seen)}, extra {sorted(seen - known)}")
    return sorted(set(committed) | set(live))


def write_fomc_days(path: Path, days: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["decision_date"])
        for day in days:
            writer.writerow([day])


# --- perpetual funding -------------------------------------------------------------
#: Complete-day rule per venue: minimum settlements per UTC day.
MIN_SETTLEMENTS = {"HYPERLIQUID": 22, "DYDX": 22, "BYBIT": 3, "BINANCE": 3, "OKX": 3}
VENUE_PREFIX = {"HYPERLIQUID": "HL", "BYBIT": "BY", "BINANCE": "BN", "OKX": "OK", "DYDX": "DY"}


def daily_funding(records: Iterable[dict[str, Any]]) -> dict[tuple[str, str, str], float]:
    """(prefix, coin, day) -> funding paid by longs over the UTC day.

    A settlement at 00:00 pays for the previous day, hence the one-millisecond
    shift before taking the date. Incomplete days are dropped.
    """
    from datetime import datetime, timezone
    sums: dict[tuple[str, str, str], list[float]] = {}
    for item in records:
        prefix = VENUE_PREFIX.get(item.get("venue", ""))
        if prefix is None:
            continue
        day = datetime.fromtimestamp((item["time_ms"] - 1) / 1000, tz=timezone.utc).date().isoformat()
        sums.setdefault((prefix, item["coin"], day), []).append(item["rate"])
    minimum = {VENUE_PREFIX[venue]: count for venue, count in MIN_SETTLEMENTS.items()}
    return {key: sum(values) for key, values in sums.items() if len(values) >= minimum[key[0]]}


def daily_marks(universe: Iterable[dict[str, Any]]) -> dict[tuple[str, str], tuple[float, float]]:
    """(coin, day) -> (last Hyperliquid mark of the day, day notional volume)."""
    marks: dict[tuple[str, str], tuple[str, float, float]] = {}
    for key, item in universe:
        hour, coin = key.split("|")
        day = hour[:10]
        current = marks.get((coin, day))
        if current is None or hour >= current[0]:
            marks[(coin, day)] = (hour, item["mark"], item["day_notional_volume"] or 0.0)
    return {key: (mark, volume) for key, (_, mark, volume) in marks.items()}


def perp_forward_rows(committed: PricePanel, funding: dict[tuple[str, str, str], float],
                      marks: dict[tuple[str, str], tuple[float, float]]) -> list[dict[str, Any]]:
    """Forward days for every venue.coin already in the panel (prices: Hyperliquid
    mark as the close of both legs, flagged ``price_proxy`` for non-HL venues)."""
    last = committed.dates[-1] if committed.dates else ""
    rows = []
    for (prefix, coin, day), carry in sorted(funding.items()):
        symbol = f"{prefix}.{coin}"
        if day <= last or symbol not in committed.symbols or (coin, day) not in marks:
            continue
        price, volume = marks[(coin, day)]
        if price <= 0:
            continue
        row = {"date": day, "symbol": symbol, "open": price, "high": price, "low": price,
               "close": price, "adj_close": price, "volume": volume, "carry_rate": carry}
        if prefix != "HL":
            row["price_proxy"] = 1.0
        rows.append(row)
    return rows
