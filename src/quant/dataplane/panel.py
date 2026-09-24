"""Normalized read interface over a daily multi-asset price panel.

The panel is the only way research and the desk are allowed to see prices, for
two reasons:

* every read is aligned on dates where *all* requested symbols exist, so a
  cross-sectional computation cannot silently compare different days;
* windows are explicit, so the point-in-time boundary between research data and
  desk-reserved data is enforced in code rather than by convention.
"""

from __future__ import annotations

import csv
import gzip
import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Window:
    """A named, inclusive date range carved out of a panel."""

    name: str
    start: str
    end: str

    def contains(self, date: str) -> bool:
        return self.start <= date <= self.end

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "start": self.start, "end": self.end}


class PricePanel:
    """Daily bars keyed by ``(date, symbol)``.

    ``adj_close`` drives the adjusted price basis used by research, modelled
    execution and marks.  Duplicate input keys are retained as validation
    evidence instead of being silently overwritten by the mapping below.

    Columns beyond ``FIELDS`` are point-in-time *features* observed on the same
    ``(date, symbol)`` key (for example a futures carry estimate). They travel
    with the bar through ``restrict``/``write`` so a feature can never be read
    from a date the price itself could not be read from. An empty cell means
    "not observed", never zero.
    """

    FIELDS = ("open", "high", "low", "close", "adj_close", "volume")
    _KEYS = ("date", "symbol")

    def __init__(self, rows: list[dict[str, object]]):
        self.bars: dict[tuple[str, str], dict[str, float]] = {}
        self.features: dict[tuple[str, str], dict[str, float]] = {}
        self.duplicate_keys: list[str] = []
        symbols: set[str] = set()
        dates: set[str] = set()
        feature_names: set[str] = set()
        for row in rows:
            date, symbol = str(row["date"]), str(row["symbol"])
            key = (date, symbol)
            if key in self.bars:
                self.duplicate_keys.append(f"{date}:{symbol}")
            self.bars[key] = {field: float(row[field]) for field in self.FIELDS}
            extra = {name: float(value) for name, value in row.items()
                     if name not in self.FIELDS and name not in self._KEYS
                     and value not in (None, "")}
            if extra:
                self.features[key] = extra
                feature_names.update(extra)
            elif key in self.features:
                del self.features[key]
            symbols.add(symbol)
            dates.add(date)
        self.feature_names = sorted(feature_names)
        self.symbols = sorted(symbols)
        self.dates = sorted(dates)
        # Alignment is recomputed for every signal evaluation otherwise, which
        # dominates the cost of a research grid. The panel is immutable once
        # constructed, so caching it is safe.
        self._aligned: dict[tuple[str, ...], list[str]] = {}
        self._index: dict[tuple[str, ...], dict[str, int]] = {}
        self._symbol_dates: dict[str, list[str]] = {}
        #: Derived per-symbol series (signals) computed once per immutable panel.
        self.derived: dict[tuple, object] = {}

    @classmethod
    def load(cls, path: Path) -> "PricePanel":
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
                return cls(list(csv.DictReader(handle)))
        with path.open(encoding="utf-8") as handle:
            return cls(list(csv.DictReader(handle)))

    @staticmethod
    def _format(field: str, value: float) -> str:
        """Six decimals holds any traded price exactly enough; shares are integral."""
        return str(int(round(value))) if field == "volume" else f"{value:.6f}"

    def write(self, path: Path) -> None:
        """Deterministic bytes: ``.gz`` output carries no timestamp, so the
        fingerprint of a rewrite of identical data is identical."""
        path.parent.mkdir(parents=True, exist_ok=True)
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer, lineterminator="\r\n")
        writer.writerow(self._KEYS + self.FIELDS + tuple(self.feature_names))
        for date in self.dates:
            for symbol in self.symbols:
                bar = self.bars.get((date, symbol))
                if bar is None:
                    continue
                extra = self.features.get((date, symbol), {})
                writer.writerow([date, symbol]
                                + [self._format(f, bar[f]) for f in self.FIELDS]
                                + [f"{extra[name]:.6f}" if name in extra else ""
                                   for name in self.feature_names])
        payload = buffer.getvalue().encode("utf-8")
        if path.suffix == ".gz":
            with path.open("wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as handle:
                    handle.write(payload)
        else:
            path.write_bytes(payload)

    # --- views -------------------------------------------------------------
    def aligned_dates(self, symbols: Iterable[str]) -> list[str]:
        key = tuple(sorted(set(symbols)))
        cached = self._aligned.get(key)
        if cached is None:
            cached = [date for date in self.dates
                      if all((date, symbol) in self.bars for symbol in key)]
            self._aligned[key] = cached
            self._index[key] = {date: position for position, date in enumerate(cached)}
        return cached

    def aligned_index(self, symbols: Iterable[str], date: str) -> int | None:
        """Position of ``date`` in the aligned series, or None if it is not a session."""
        key = tuple(sorted(set(symbols)))
        if key not in self._index:
            self.aligned_dates(key)
        return self._index[key].get(date)

    def dates_for(self, symbol: str) -> list[str]:
        cached = self._symbol_dates.get(symbol)
        if cached is None:
            cached = [date for date in self.dates if (date, symbol) in self.bars]
            self._symbol_dates[symbol] = cached
        return cached

    def has(self, date: str, symbol: str) -> bool:
        return (date, symbol) in self.bars

    def price(self, date: str, symbol: str, field: str = "adj_close") -> float:
        return self.bars[(date, symbol)][field]

    def feature(self, date: str, symbol: str, name: str) -> float | None:
        """A point-in-time feature, or None when it was not observed that session."""
        return self.features.get((date, symbol), {}).get(name)

    def adjusted(self, date: str, symbol: str, field: str = "open") -> float:
        """Put raw open/high/low on the same adjusted basis as ``adj_close``.

        Research returns, modelled fills and Book marks must share one price
        basis, or the Book drifts against its own evidence every time a dividend
        or split lands.
        """
        bar = self.bars[(date, symbol)]
        if bar["close"] <= 0:
            return bar["adj_close"]
        return bar[field] * (bar["adj_close"] / bar["close"])

    def restrict(self, start: str | None = None, end: str | None = None,
                 symbols: Iterable[str] | None = None) -> "PricePanel":
        wanted = set(symbols) if symbols is not None else None
        rows = []
        for (date, symbol), bar in self.bars.items():
            if start is not None and date < start:
                continue
            if end is not None and date > end:
                continue
            if wanted is not None and symbol not in wanted:
                continue
            rows.append({"date": date, "symbol": symbol, **bar,
                         **self.features.get((date, symbol), {})})
        return PricePanel(rows)

    def window(self, window: Window, symbols: Iterable[str] | None = None) -> "PricePanel":
        return self.restrict(window.start, window.end, symbols)

    def returns(self, symbols: Iterable[str]) -> tuple[list[str], dict[str, list[float]]]:
        """Aligned simple returns. ``dates[i]`` is the date the return is earned."""
        wanted = list(symbols)
        dates = self.aligned_dates(wanted)
        series = {symbol: [] for symbol in wanted}
        for index in range(1, len(dates)):
            previous, current = dates[index - 1], dates[index]
            for symbol in wanted:
                before = self.price(previous, symbol)
                series[symbol].append(self.price(current, symbol) / before - 1.0 if before else 0.0)
        return dates[1:], series

    def split(self, fractions: dict[str, float],
              symbols: Iterable[str] | None = None) -> dict[str, Window]:
        """Carve the panel into contiguous named windows by fraction of dates.

        The fractions must sum to 1. Windows never overlap, which is what makes
        a desk-reserved holdout enforceable.
        """
        if abs(sum(fractions.values()) - 1.0) > 1e-9:
            raise ValueError("window fractions must sum to 1")
        dates = self.aligned_dates(symbols) if symbols is not None else self.dates
        windows: dict[str, Window] = {}
        cursor = 0
        names = list(fractions)
        for position, name in enumerate(names):
            if position == len(names) - 1:
                stop = len(dates)
            else:
                stop = cursor + max(1, int(math.floor(len(dates) * fractions[name])))
            stop = min(stop, len(dates))
            if cursor >= stop:
                raise ValueError(f"window {name} is empty")
            windows[name] = Window(name, dates[cursor], dates[stop - 1])
            cursor = stop
        return windows
