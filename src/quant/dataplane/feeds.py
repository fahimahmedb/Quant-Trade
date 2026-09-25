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


def _stream_files(path: Path) -> list[Path]:
    """A stream is ``<name>.jsonl`` (legacy) and/or monthly shards in ``<name>/``."""
    shards = sorted(path.with_suffix("").glob("*.jsonl")) if path.with_suffix("").is_dir() else []
    return ([path] if path.exists() else []) + shards


def read_latest(path: Path) -> dict[str, dict[str, Any]]:
    """Latest version of every key (restatements win), with ``_observed_at``."""
    latest: dict[str, tuple[str, dict[str, Any]]] = {}
    for shard in _stream_files(path):
        for line in shard.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            base = item["key"].split("#restated@")[0]
            stamp = item.get("observed_at", "")
            if base not in latest or stamp >= latest[base][0]:
                latest[base] = (stamp, item["record"])
    return {key: {**record, "_observed_at": stamp} for key, (stamp, record) in latest.items()}


def checkout_feeds(repo: Path, destination: Path, branch: str = FEEDS_BRANCH) -> Path:
    """Materialise ``data/feeds`` from the data branch (git is the only egress)."""
    import shutil
    shutil.rmtree(destination, ignore_errors=True)     # never mix in stale files
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
def _final(record: dict[str, Any]) -> bool:
    """Only bars observed after their session's close are point-in-time final
    (records collected before that rule existed are filtered here)."""
    from datetime import datetime, timedelta, timezone
    observed = record.get("_observed_at")
    if not observed:
        return False
    close = (datetime.fromisoformat(record["date"]).replace(tzinfo=timezone.utc)
             + timedelta(hours=23))
    return datetime.fromisoformat(observed) >= close


def etf_forward_rows(committed: PricePanel, feed: dict[str, dict[str, Any]],
                     symbols: Iterable[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """New complete sessions for ``symbols``, rebased at the seam date.

    A session is appended only when every symbol has a final bar that day and
    the feed also holds the seam date for every symbol; the first incomplete
    session stops the append and is reported (a gap is never bridged).
    """
    symbols = list(symbols)
    info: dict[str, Any] = {}
    last = max(committed.dates_for(symbols[0])) if committed.dates_for(symbols[0]) else None
    if last is None:
        return [], {"blocked": "empty committed panel"}
    by_symbol: dict[str, dict[str, dict[str, Any]]] = {}
    for record in feed.values():
        if record.get("symbol") in symbols and _final(record):
            by_symbol.setdefault(record["symbol"], {})[record["date"]] = record
    factors = {}
    for symbol in symbols:
        seam = by_symbol.get(symbol, {}).get(last)
        if seam is None or not committed.has(last, symbol) or seam["adj_close"] <= 0:
            return [], {"blocked": f"feed does not hold the seam date {last} for {symbol}"}
        factors[symbol] = committed.price(last, symbol) / seam["adj_close"]
    new_dates = sorted({day for bars in by_symbol.values() for day in bars if day > last})
    rows = []
    for day in new_dates:
        missing = [symbol for symbol in symbols if day not in by_symbol.get(symbol, {})]
        if missing:
            info = {"blocked_at": day, "missing_symbols": missing}
            break
        for symbol in symbols:
            bar = by_symbol[symbol][day]
            rows.append({"date": day, "symbol": symbol, "open": bar["open"],
                         "high": bar["high"], "low": bar["low"], "close": bar["close"],
                         "adj_close": bar["adj_close"] * factors[symbol],
                         "volume": bar["volume"]})
    return rows, info


def extend_panel(committed: PricePanel, rows: list[dict[str, Any]]) -> PricePanel:
    existing = [{"date": day, "symbol": symbol, **bar,
                 **committed.features.get((day, symbol), {})}
                for (day, symbol), bar in committed.bars.items()]
    return PricePanel(existing + rows)


# --- FOMC schedule -----------------------------------------------------------------
def merged_fomc_days(committed: list[str], feed: dict[str, dict[str, Any]],
                     as_of: str | None = None) -> list[str]:
    """Reconcile the committed schedule with the Fed's published one.

    Past decision days are history and must agree; a disagreement refuses the
    merge. Future days follow the live schedule, so a moved or cancelled future
    meeting is removed instead of lingering as a phantom FOMC day.
    """
    live = sorted(record["decision_date"] for record in feed.values())
    if not live:
        return committed
    as_of = as_of or max(record.get("_observed_at", "")[:10] for record in feed.values())
    overlap = [day for day in committed if live[0] <= day <= as_of]
    seen = [day for day in live if day <= as_of]
    if set(overlap) != set(seen):
        raise DataUnavailable(f"FOMC feed contradicts the committed schedule: "
                              f"missing {sorted(set(overlap) - set(seen))}, "
                              f"extra {sorted(set(seen) - set(overlap))}")
    past = [day for day in committed if day <= as_of]
    return sorted(set(past) | {day for day in live if day > as_of})


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


def daily_funding(records: Iterable[dict[str, Any]],
                  as_of: str | None = None) -> dict[tuple[str, str, str], float]:
    """(prefix, coin, day) -> funding paid by longs over the UTC day.

    Settlement timestamps are rounded to the hour first (venue timestamps carry
    millisecond jitter). Day attribution follows each venue's convention in the
    committed history: Hyperliquid prints are grouped by their own date
    (00:00..23:00), 8-hourly venues attribute the 00:00 settlement to the
    previous day. A day is accepted only once it has ended (as of the newest
    observation) and carries the number of settlements its interval implies.
    """
    from datetime import datetime, timedelta, timezone
    hour_ms = 3_600_000
    grouped: dict[tuple[str, str, str], list[tuple[int, float]]] = {}
    newest = as_of
    for item in records:
        prefix = VENUE_PREFIX.get(item.get("venue", ""))
        if prefix is None:
            continue
        stamp = int(round(item["time_ms"] / hour_ms)) * hour_ms
        shifted = stamp if prefix == "HL" else stamp - 1
        day = datetime.fromtimestamp(shifted / 1000, tz=timezone.utc).date().isoformat()
        grouped.setdefault((prefix, item["coin"], day), []).append((stamp, item["rate"]))
        observed = item.get("_observed_at")
        if observed and (newest is None or observed > newest):
            newest = observed
    out = {}
    for key, values in grouped.items():
        day_end = datetime.fromisoformat(key[2]).replace(tzinfo=timezone.utc) + timedelta(days=1)
        if newest is None or datetime.fromisoformat(newest) < day_end + timedelta(hours=1):
            continue                                   # the day has not finished
        stamps = sorted({stamp for stamp, _ in values})
        spacing = (min(b - a for a, b in zip(stamps, stamps[1:])) if len(stamps) > 1
                   else 8 * hour_ms)
        expected = max(1, round(24 * hour_ms / spacing))
        if len(stamps) >= expected and len(values) == len(stamps):
            out[key] = sum(rate for _, rate in values)
    return out


def daily_marks(universe: Iterable[tuple[str, dict[str, Any]]]
                ) -> dict[tuple[str, str], tuple[float, float]]:
    """(coin, day) -> (Hyperliquid mark at the close of the day, 24h volume).

    The close of day D is the first snapshot taken on D+1 between 00:00 and
    05:59 UTC; a day without such a snapshot has no close and is skipped.
    """
    from datetime import date, timedelta
    first_next: dict[tuple[str, str], tuple[str, float, float]] = {}
    for key, item in universe:
        hour, coin = key.split("|")
        if int(hour[11:13]) > 5:
            continue
        day = (date.fromisoformat(hour[:10]) - timedelta(days=1)).isoformat()
        current = first_next.get((coin, day))
        if current is None or hour < current[0]:
            first_next[(coin, day)] = (hour, item["mark"], item["day_notional_volume"] or 0.0)
    return {key: (mark, volume) for key, (_, mark, volume) in first_next.items()}


def perp_forward_rows(committed: PricePanel, funding: dict[tuple[str, str, str], float],
                      marks: dict[tuple[str, str], tuple[float, float]]) -> list[dict[str, Any]]:
    """Forward Hyperliquid days for coins already in the panel.

    Other venues are *not* appended forward: valuing them at the Hyperliquid
    mark (a perfect hedge) would enter pristine evidence as if it were real.
    Until a second venue's own prices are collected the pair lane stays flat,
    which ``sync_feeds`` reports as blocked.
    """
    last = committed.dates[-1] if committed.dates else ""
    rows = []
    for (prefix, coin, day), carry in sorted(funding.items()):
        symbol = f"{prefix}.{coin}"
        if prefix != "HL" or day <= last or symbol not in committed.symbols \
                or (coin, day) not in marks:
            continue
        price, volume = marks[(coin, day)]
        if price <= 0:
            continue
        rows.append({"date": day, "symbol": symbol, "open": price, "high": price, "low": price,
                     "close": price, "adj_close": price, "volume": volume, "carry_rate": carry})
    return rows
