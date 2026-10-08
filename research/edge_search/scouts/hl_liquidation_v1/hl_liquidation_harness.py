from __future__ import annotations

import json
import math
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

BUCKET_MS = 5_000
BASELINE_BUCKETS = 60          # 5 minutes
PRE_FEATURE_MS = 60_000       # 60 seconds
CONTROL_LOOKBACK_MS = 86_400_000  # prior 24h only
POST_HORIZON_MS = 30_000      # ONE frozen horizon
EVENT_COOLDOWN_MS = 60_000
BBO_MAX_AGE_MS = 2_000
TAKER_FEE_PER_SIDE = Decimal("0.0005")  # frozen 5 bp per side
MIN_FORCED_PURITY = Decimal("0.80")
EVENT_THRESHOLD_X = Decimal("1.00")     # forced gross >= prior 5m avg total aggressive flow
CONTROL_FLOW_RATIO_LO = Decimal("0.50")
CONTROL_FLOW_RATIO_HI = Decimal("2.00")
CONTROL_RV_RATIO_LO = Decimal("0.50")
CONTROL_RV_RATIO_HI = Decimal("2.00")

COINS = {"BTC", "ETH"}

class DataError(RuntimeError):
    pass


def D(x) -> Decimal:
    try:
        v = Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError) as e:
        raise DataError(f"invalid decimal: {x!r}") from e
    if not v.is_finite():
        raise DataError(f"non-finite decimal: {x!r}")
    return v


@dataclass(frozen=True)
class FillRow:
    block_number: int
    block_time_ms: int
    local_time_ms: int
    user: str
    coin: str
    tid: int
    time_ms: int
    px: Decimal
    sz: Decimal
    side: str
    crossed: bool
    liquidation_method: Optional[str]
    liquidated_user: Optional[str]
    mark_px: Optional[Decimal]
    dir: str


@dataclass(frozen=True)
class Trade:
    block_number: int
    coin: str
    tid: int
    time_ms: int
    available_ms: int
    px: Decimal
    sz: Decimal
    aggressor_side: str
    notional: Decimal
    forced_market: bool
    backstop: bool
    adl: bool

    @property
    def sign(self) -> int:
        return 1 if self.aggressor_side == "B" else -1


@dataclass
class Bucket:
    coin: str
    start_ms: int
    forced_buy: Decimal = Decimal(0)
    forced_sell: Decimal = Decimal(0)
    voluntary_buy: Decimal = Decimal(0)
    voluntary_sell: Decimal = Decimal(0)
    all_aggressive: Decimal = Decimal(0)
    last_available_ms: int = 0

    @property
    def forced_total(self) -> Decimal:
        return self.forced_buy + self.forced_sell

    @property
    def forced_signed(self) -> Decimal:
        return self.forced_buy - self.forced_sell

    @property
    def voluntary_signed(self) -> Decimal:
        return self.voluntary_buy - self.voluntary_sell

    @property
    def end_ms(self) -> int:
        return self.start_ms + BUCKET_MS


@dataclass(frozen=True)
class Bbo:
    coin: str
    time_ms: int
    bid: Decimal
    ask: Decimal
    available_ms: Optional[int] = None

    @property
    def avail_ms(self) -> int:
        return self.time_ms if self.available_ms is None else self.available_ms

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / 2


@dataclass(frozen=True)
class Event:
    coin: str
    bucket_start_ms: int
    t0_ms: int
    direction: int
    forced_norm: Decimal
    pre_return: Decimal
    pre_rv: Decimal


@dataclass(frozen=True)
class PairResult:
    event: Event
    control_start_ms: int
    forced_net_return: Decimal
    control_net_return: Decimal
    paired_diff: Decimal
    utc_day: str


def _iso_to_ms(s: str) -> int:
    if not isinstance(s, str):
        raise DataError("block_time must be ISO string")
    z = s[:-1] + "+00:00" if s.endswith("Z") else s
    dt = datetime.fromisoformat(z)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def parse_fill_blocks(lines: Iterable[str]) -> List[FillRow]:
    """Parse current node_fills_by_block JSONL. Fail closed on conflicting block rewinds.

    Duplicate identical block envelopes are folded. Events must be [user, fill].
    Only BTC/ETH rows are returned; other markets are structurally parsed enough to skip.
    """
    blocks: Dict[int, Tuple[int, str]] = {}
    out: List[FillRow] = []
    for raw in lines:
        if not raw.strip():
            continue
        obj = json.loads(raw)
        bn = int(obj["block_number"])
        bt = _iso_to_ms(obj["block_time"])
        lt = _iso_to_ms(obj["local_time"])
        fingerprint = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        if bn in blocks:
            if blocks[bn] != (bt, fingerprint):
                raise DataError(f"conflicting duplicate block {bn}")
            continue
        blocks[bn] = (bt, fingerprint)
        evs = obj.get("events")
        if not isinstance(evs, list):
            raise DataError("events must be list")
        for ev in evs:
            if not (isinstance(ev, list) and len(ev) == 2 and isinstance(ev[1], dict)):
                raise DataError("fill event must be [user, fill]")
            user, f = str(ev[0]).lower(), ev[1]
            coin = str(f.get("coin"))
            if coin not in COINS:
                continue
            liq = f.get("liquidation")
            method = liquidated_user = None
            mark_px = None
            if liq is not None:
                if not isinstance(liq, dict):
                    raise DataError("liquidation must be object")
                method = str(liq.get("method"))
                if method not in {"market", "backstop"}:
                    raise DataError(f"unknown liquidation method {method!r}")
                lu = liq.get("liquidatedUser")
                liquidated_user = str(lu).lower() if lu is not None else None
                mark_px = D(liq["markPx"])
            side = str(f["side"])
            if side not in {"B", "A"}:
                raise DataError("side must be B/A")
            out.append(FillRow(
                block_number=bn,
                block_time_ms=bt,
                local_time_ms=lt,
                user=user,
                coin=coin,
                tid=int(f["tid"]),
                time_ms=int(f["time"]),
                px=D(f["px"]),
                sz=D(f["sz"]),
                side=side,
                crossed=bool(f["crossed"]),
                liquidation_method=method,
                liquidated_user=liquidated_user,
                mark_px=mark_px,
                dir=str(f.get("dir", "")),
            ))
    return out


def validate_block_continuity(lines: Iterable[str]) -> Tuple[int, int, int]:
    """Return (first,last,count) and fail closed on any missing sequential block.

    Run this on the complete concatenation of node_fills_by_block capture files.
    Duplicate identical block numbers are allowed here because parse_fill_blocks validates identity.
    """
    seen = {}
    for raw in lines:
        if not raw.strip():
            continue
        obj = json.loads(raw)
        bn = int(obj["block_number"])
        bt = str(obj["block_time"])
        if bn in seen and seen[bn] != bt:
            raise DataError(f"conflicting duplicate block {bn}")
        seen[bn] = bt
    if not seen:
        raise DataError("empty block capture")
    nums = sorted(seen)
    for a,b in zip(nums, nums[1:]):
        if b != a + 1:
            raise DataError(f"block gap {a}->{b}")
    return nums[0], nums[-1], len(nums)

def canonicalize_trades(rows: Sequence[FillRow]) -> List[Trade]:
    """Collapse the maker/taker pair to one canonical print using (block, coin, tid)."""
    groups: Dict[Tuple[int, str, int], List[FillRow]] = defaultdict(list)
    for r in rows:
        groups[(r.block_number, r.coin, r.tid)].append(r)
    out: List[Trade] = []
    for key in sorted(groups):
        # exact row duplicates may occur after replay/restart; fold them first
        uniq: Dict[Tuple, FillRow] = {}
        for r in groups[key]:
            rk = (r.user, r.time_ms, r.px, r.sz, r.side, r.crossed,
                  r.liquidation_method, r.liquidated_user, r.mark_px)
            uniq[rk] = r
        rs = list(uniq.values())
        methods = {r.liquidation_method for r in rs if r.liquidation_method is not None}
        if len(methods) > 1:
            raise DataError(f"conflicting liquidation methods {key}")
        method = next(iter(methods)) if methods else None
        for r in rs[1:]:
            if (r.time_ms, r.px, r.sz) != (rs[0].time_ms, rs[0].px, rs[0].sz):
                raise DataError(f"paired fill disagreement {key}")
        takers = [r for r in rs if r.crossed]
        if method == "backstop":
            # Backstop is forced but does not aggress the public book; retain only as an excluded diagnostic.
            t = sorted(rs, key=lambda r: (r.user, r.side))[0]
        else:
            if len(takers) != 1:
                raise DataError(f"trade {key} must have exactly one taker after dedup")
            t = takers[0]
        forced_market = method == "market"
        backstop = method == "backstop"
        adl = any(r.dir == "Auto-Deleveraging" for r in rs)
        out.append(Trade(
            block_number=t.block_number,
            coin=t.coin,
            tid=t.tid,
            time_ms=t.time_ms,
            available_ms=max(r.local_time_ms for r in rs),
            px=t.px,
            sz=t.sz,
            aggressor_side=t.side,
            notional=t.px * t.sz,
            forced_market=forced_market,
            backstop=backstop,
            adl=adl,
        ))
    return sorted(out, key=lambda x: (x.time_ms, x.block_number, x.coin, x.tid))


def bucketize(trades: Sequence[Trade]) -> Dict[Tuple[str, int], Bucket]:
    b: Dict[Tuple[str, int], Bucket] = {}
    for t in trades:
        if t.backstop or t.adl:
            continue  # not the market-liquidation-vs-voluntary mechanism
        s = (t.time_ms // BUCKET_MS) * BUCKET_MS
        k = (t.coin, s)
        x = b.setdefault(k, Bucket(t.coin, s))
        x.all_aggressive += t.notional
        x.last_available_ms = max(x.last_available_ms, t.available_ms)
        if t.forced_market:
            if t.aggressor_side == "B":
                x.forced_buy += t.notional
            else:
                x.forced_sell += t.notional
        else:
            if t.aggressor_side == "B":
                x.voluntary_buy += t.notional
            else:
                x.voluntary_sell += t.notional
    return b


def parse_ws_bbo(lines: Iterable[str]) -> List[Bbo]:
    out = []
    seen = set()
    for raw in lines:
        if not raw.strip():
            continue
        obj = json.loads(raw)
        if obj.get("channel") != "bbo":
            continue
        d = obj["data"]
        coin = str(d["coin"])
        if coin not in COINS:
            continue
        arr = d["bbo"]
        if not isinstance(arr, list) or len(arr) != 2 or arr[0] is None or arr[1] is None:
            continue
        bid, ask = D(arr[0]["px"]), D(arr[1]["px"])
        if bid <= 0 or ask <= bid:
            raise DataError("invalid BBO")
        available_ms = int(obj.get("_recv_ns", int(d["time"]) * 1_000_000)) // 1_000_000
        k = (coin, int(d["time"]), bid, ask, available_ms)
        if k in seen:
            continue
        seen.add(k)
        out.append(Bbo(coin, int(d["time"]), bid, ask, available_ms))
    return sorted(out, key=lambda x: (x.coin, x.avail_ms, x.time_ms))


def _bbo_at(bbos: Sequence[Bbo], coin: str, t: int) -> Optional[Bbo]:
    # Deliberately only observations at or before t: no after-t0 leakage.
    best = None
    for b in bbos:
        if b.coin != coin:
            continue
        if b.avail_ms <= t:
            if best is None or b.avail_ms > best.avail_ms or (b.avail_ms == best.avail_ms and b.time_ms > best.time_ms):
                best = b
    if best is None or t - best.avail_ms > BBO_MAX_AGE_MS:
        return None
    return best


def _pre_features(bbos: Sequence[Bbo], coin: str, t0: int) -> Optional[Tuple[Decimal, Decimal]]:
    pts = [b for b in bbos if b.coin == coin and t0 - PRE_FEATURE_MS <= b.avail_ms <= t0]
    if len(pts) < 2:
        return None
    # strictly no observation later than t0; dedup timestamps using the last update
    by_t = {(p.avail_ms, p.time_ms): p for p in pts}
    seq = [by_t[k] for k in sorted(by_t)]
    p0, p1 = seq[0].mid, seq[-1].mid
    pre_ret = (p1 / p0) - 1
    rv = Decimal(0)
    prev = seq[0].mid
    for p in seq[1:]:
        r = (p.mid / prev) - 1
        rv += abs(r)
        prev = p.mid
    return pre_ret, rv


def detect_events(buckets: Dict[Tuple[str, int], Bucket], bbos: Sequence[Bbo]) -> List[Event]:
    by_coin: Dict[str, Dict[int, Bucket]] = defaultdict(dict)
    for (coin, s), x in buckets.items():
        by_coin[coin][s] = x
    events: List[Event] = []
    for coin in sorted(COINS):
        if not by_coin[coin]:
            continue
        starts = sorted(by_coin[coin])
        lo = min(starts)
        hi = max(starts)
        last_event_t0 = -10**30
        s = lo
        while s <= hi:
            x = by_coin[coin].get(s, Bucket(coin, s))
            prior = [by_coin[coin].get(s - i * BUCKET_MS, Bucket(coin, s - i * BUCKET_MS)).all_aggressive
                     for i in range(1, BASELINE_BUCKETS + 1)]
            baseline = sum(prior, Decimal(0)) / Decimal(BASELINE_BUCKETS)
            ft = x.forced_total
            if baseline > 0 and ft > 0 and x.end_ms - last_event_t0 >= EVENT_COOLDOWN_MS:
                purity = abs(x.forced_signed) / ft
                if purity >= MIN_FORCED_PURITY and ft >= EVENT_THRESHOLD_X * baseline:
                    t0 = max(x.end_ms, x.last_available_ms)
                    feat = _pre_features(bbos, coin, t0)
                    if feat is not None and _bbo_at(bbos, coin, t0) is not None:
                        direction = 1 if x.forced_signed > 0 else -1
                        events.append(Event(coin, s, t0, direction, x.forced_signed / baseline, feat[0], feat[1]))
                        last_event_t0 = t0
            s += BUCKET_MS
    return events


def _voluntary_norm(x: Bucket, baseline: Decimal) -> Decimal:
    return x.voluntary_signed / baseline if baseline > 0 else Decimal(0)


def match_controls(events: Sequence[Event], buckets: Dict[Tuple[str, int], Bucket], bbos: Sequence[Bbo]) -> List[Tuple[Event, int]]:
    used = set()
    matches = []
    for e in sorted(events, key=lambda z: z.t0_ms):
        best_t0 = None
        best_bucket = None
        best_score = None
        start = e.bucket_start_ms - CONTROL_LOOKBACK_MS
        s = start - (start % BUCKET_MS)
        while s < e.bucket_start_ms:
            k = (e.coin, s)
            if k in used:
                s += BUCKET_MS; continue
            x = buckets.get(k, Bucket(e.coin, s))
            if x.forced_total != 0 or x.voluntary_signed == 0:
                s += BUCKET_MS; continue
            # compute the same trailing baseline at the candidate control time
            prior = [buckets.get((e.coin, s - i * BUCKET_MS), Bucket(e.coin, s - i * BUCKET_MS)).all_aggressive
                     for i in range(1, BASELINE_BUCKETS + 1)]
            baseline = sum(prior, Decimal(0)) / Decimal(BASELINE_BUCKETS)
            if baseline <= 0:
                s += BUCKET_MS; continue
            vn = _voluntary_norm(x, baseline)
            if (1 if vn > 0 else -1) != e.direction:
                s += BUCKET_MS; continue
            ratio = abs(vn / e.forced_norm)
            if not (CONTROL_FLOW_RATIO_LO <= ratio <= CONTROL_FLOW_RATIO_HI):
                s += BUCKET_MS; continue
            ct0 = max(x.end_ms, x.last_available_ms)
            feat = _pre_features(bbos, e.coin, ct0)
            if feat is None or _bbo_at(bbos, e.coin, ct0) is None:
                s += BUCKET_MS; continue
            cr, cv = feat
            if e.pre_rv <= 0 or cv <= 0:
                s += BUCKET_MS; continue
            rvr = cv / e.pre_rv
            if not (CONTROL_RV_RATIO_LO <= rvr <= CONTROL_RV_RATIO_HI):
                s += BUCKET_MS; continue
            if abs(cr - e.pre_return) > e.pre_rv:
                s += BUCKET_MS; continue
            score = abs(ratio - 1) + abs(rvr - 1) + abs(cr - e.pre_return) / e.pre_rv
            if best_score is None or score < best_score or (score == best_score and (best_bucket is None or s < best_bucket)):
                best_t0, best_bucket, best_score = ct0, s, score
            s += BUCKET_MS
        if best_t0 is not None and best_bucket is not None:
            used.add((e.coin, best_bucket))
            matches.append((e, best_t0))
    return matches


def executable_return(bbos: Sequence[Bbo], coin: str, t0: int, direction: int) -> Optional[Decimal]:
    a = _bbo_at(bbos, coin, t0)
    z = _bbo_at(bbos, coin, t0 + POST_HORIZON_MS)
    if a is None or z is None:
        return None
    if direction > 0:
        entry, exit_ = a.ask, z.bid
    else:
        entry, exit_ = a.bid, z.ask
        # short return expressed on entry notional
        gross = (entry - exit_) / entry
        return gross - 2 * TAKER_FEE_PER_SIDE
    gross = (exit_ - entry) / entry
    return gross - 2 * TAKER_FEE_PER_SIDE


def score_pairs(matches: Sequence[Tuple[Event, int]], bbos: Sequence[Bbo]) -> List[PairResult]:
    out = []
    for e, ct0 in matches:
        fr = executable_return(bbos, e.coin, e.t0_ms, e.direction)
        cr = executable_return(bbos, e.coin, ct0, e.direction)
        if fr is None or cr is None:
            continue
        day = datetime.fromtimestamp(e.t0_ms / 1000, tz=timezone.utc).date().isoformat()
        out.append(PairResult(e, ct0, fr, cr, fr - cr, day))
    return out


def cluster_t(results: Sequence[PairResult]) -> Tuple[Decimal, Decimal, int]:
    """Mean paired difference and UTC-day cluster-robust t for the mean."""
    n = len(results)
    if n == 0:
        raise DataError("no results")
    mu = sum((r.paired_diff for r in results), Decimal(0)) / Decimal(n)
    clusters: Dict[str, Decimal] = defaultdict(Decimal)
    counts: Dict[str, int] = defaultdict(int)
    for r in results:
        clusters[r.utc_day] += r.paired_diff - mu
        counts[r.utc_day] += 1
    g = len(clusters)
    if g < 2:
        return mu, Decimal(0), g
    meat = sum((v * v for v in clusters.values()), Decimal(0))
    # finite-cluster correction G/(G-1); variance of mean = meat/n^2
    var = (Decimal(g) / Decimal(g - 1)) * meat / Decimal(n * n)
    if var <= 0:
        return mu, Decimal(0), g
    se = var.sqrt()
    return mu, mu / se, g


def decision(results: Sequence[PairResult]) -> str:
    """Frozen decision rule; no parameter tuning is permitted after outcome exposure."""
    n = len(results)
    if n < 50:
        return "KEEP_UNDERPOWERED"
    mu, t, g = cluster_t(results)
    if g < 10:
        return "KEEP_UNDERPOWERED"
    forced_mean = sum((r.forced_net_return for r in results), Decimal(0)) / Decimal(n)
    by_day = defaultdict(list)
    for r in results:
        by_day[r.utc_day].append(r.paired_diff)
    positive_days = sum(1 for xs in by_day.values() if sum(xs, Decimal(0)) / Decimal(len(xs)) > 0)
    pos_share = Decimal(positive_days) / Decimal(len(by_day))
    # PROMOTE requires incremental +5bp, positive executable absolute return,
    # one-sided-ish t >=2, and broad day support. KILL only with a clear negative upper bound proxy.
    if mu >= Decimal("0.0005") and forced_mean > 0 and t >= Decimal("2.0") and pos_share >= Decimal("0.60"):
        return "PROMOTE"
    if t <= Decimal("-1.645"):
        return "KILL"
    return "KEEP"


def _frozen_config() -> dict:
    return {
        "coins": sorted(COINS),
        "bucket_ms": BUCKET_MS,
        "baseline_buckets": BASELINE_BUCKETS,
        "pre_feature_ms": PRE_FEATURE_MS,
        "control_lookback_ms": CONTROL_LOOKBACK_MS,
        "post_horizon_ms": POST_HORIZON_MS,
        "event_cooldown_ms": EVENT_COOLDOWN_MS,
        "bbo_max_age_ms": BBO_MAX_AGE_MS,
        "taker_fee_per_side": str(TAKER_FEE_PER_SIDE),
        "min_forced_purity": str(MIN_FORCED_PURITY),
        "event_threshold_x": str(EVENT_THRESHOLD_X),
        "control_flow_ratio": [str(CONTROL_FLOW_RATIO_LO), str(CONTROL_FLOW_RATIO_HI)],
        "control_rv_ratio": [str(CONTROL_RV_RATIO_LO), str(CONTROL_RV_RATIO_HI)],
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Frozen Hyperliquid forced-liquidation discriminator")
    ap.add_argument("node_fills_jsonl", help="complete node_fills_by_block JSONL capture")
    ap.add_argument("market_ws_jsonl", help="raw prospective public WS capture from record_hl_public_ws.py")
    ap.add_argument("result_json", help="new result path; must not already exist")
    args = ap.parse_args(argv)

    with open(args.node_fills_jsonl, encoding="utf-8") as f:
        fill_lines = f.readlines()
    first_block, last_block, block_count = validate_block_continuity(fill_lines)
    rows = parse_fill_blocks(fill_lines)
    trades = canonicalize_trades(rows)
    buckets = bucketize(trades)
    with open(args.market_ws_jsonl, encoding="utf-8") as f:
        bbos = parse_ws_bbo(f)
    events = detect_events(buckets, bbos)
    matches = match_controls(events, buckets, bbos)
    results = score_pairs(matches, bbos)
    verdict = decision(results)
    payload = {
        "frozen_config": _frozen_config(),
        "capture": {"first_block": first_block, "last_block": last_block, "block_count": block_count},
        "counts": {"fill_rows": len(rows), "canonical_trades": len(trades), "events": len(events), "matches": len(matches), "scored_pairs": len(results)},
        "decision": verdict,
    }
    if results:
        mu, t, g = cluster_t(results)
        payload["primary"] = {"mean_paired_net_return_diff": str(mu), "utc_day_cluster_t": str(t), "utc_day_clusters": g}
        payload["forced_mean_net_return"] = str(sum((r.forced_net_return for r in results), Decimal(0)) / Decimal(len(results)))
    with open(args.result_json, "x", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
