"""Shared helpers for the settlement-liquidity 30-day falsification (research only, no orders).

All endpoints are public and unauthenticated. Nothing here places, signs or cancels orders.
REAL_CAPITAL_AUTHORIZED = FALSE.
"""
import datetime as dt
import gzip
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "raw")  # large caches; gitignored-by-convention (see README in data/)
os.makedirs(RAW, exist_ok=True)

# Predeclared primary window (UTC, closedTime of the market). Frozen before any economics.
PRIMARY_START = dt.datetime(2026, 8, 30, tzinfo=dt.timezone.utc)
PRIMARY_END = dt.datetime(2026, 9, 29, tzinfo=dt.timezone.utc)  # exclusive; 30 complete days
MIN_VOLUME = 1000.0  # lifetime USDC volume (gamma volumeNum), same as A5/A7 screens

UA = {"User-Agent": "Mozilla/5.0 (quant-research; settlement-liquidity falsification)"}


def get(url, tries=6, timeout=60, allow_404=False):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404 and allow_404:
                return None
            if e.code in (400, 404, 422):
                raise
            time.sleep(1.5 * (i + 1))
        except Exception as e:  # network hiccup
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"GET failed after {tries}: {url}: {last}")


def post(url, payload, tries=6, timeout=60):
    body = json.dumps(payload).encode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers={**UA, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"POST failed after {tries}: {url}: {last}")


def parse_ts(s):
    """Parse gamma/ESPN/MLB timestamps to epoch seconds (float). None-safe."""
    if s is None or s == "":
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = s.strip().replace(" ", "T")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    if s.endswith("+00"):
        s = s + ":00"
    # trim sub-microsecond digits
    if "." in s:
        head, tail = s.split(".", 1)
        frac = ""
        rest = ""
        for j, ch in enumerate(tail):
            if ch.isdigit():
                frac += ch
            else:
                rest = tail[j:]
                break
        s = head + "." + frac[:6].ljust(6, "0") + rest
    d = dt.datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.timestamp()


def iso(ts):
    if ts is None:
        return None
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_jsonl_gz(path, rows):
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")


def read_jsonl_gz(path):
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
