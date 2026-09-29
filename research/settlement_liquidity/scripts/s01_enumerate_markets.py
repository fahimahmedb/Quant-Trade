"""Step 1: enumerate every CLOSED Polymarket market whose closedTime falls in a UTC window.

Usage: python3 s01_enumerate_markets.py 2026-08-30 2026-09-29 [out_name]
Pages gamma /markets/keyset ordered by closedTime desc, volume_num_min = MIN_VOLUME.
Keeps a compact record per market (no outcome-dependent filtering happens here).

Resumable: pages are appended to data/raw/<out_name>.partial.jsonl and the keyset cursor is saved in
data/raw/<out_name>.cursor after every page; a re-run continues from the saved cursor. When finished
the final file data/raw/<out_name>.jsonl.gz is written and the partial files are removed.
"""
import datetime as dt
import json
import os
import sys
import urllib.parse

from common import MIN_VOLUME, RAW, get, parse_ts, write_jsonl_gz

KEEP = ["id", "conditionId", "question", "slug", "closedTime", "endDate", "startDate", "createdAt", "volumeNum",
        "outcomes", "outcomePrices", "clobTokenIds", "sportsMarketType", "line", "gameStartTime",
        "umaResolutionStatuses", "umaResolutionStatus", "umaEndDate", "automaticallyResolved", "resolvedBy",
        "negRisk", "negRiskMarketID", "feeSchedule", "feesEnabled", "feeType", "orderPriceMinTickSize",
        "resolutionSource", "groupItemTitle", "questionID", "customLiveness", "umaBond"]
EV_KEEP = ["id", "slug", "ticker", "title", "seriesSlug", "gameId", "finishedTimestamp", "score", "period", "ended",
           "eventDate", "startTime", "closedTime", "automaticallyResolved", "negRisk", "resolutionSource"]


def main():
    d0 = dt.datetime.fromisoformat(sys.argv[1]).replace(tzinfo=dt.timezone.utc).timestamp()
    d1 = dt.datetime.fromisoformat(sys.argv[2]).replace(tzinfo=dt.timezone.utc).timestamp()
    name = sys.argv[3] if len(sys.argv) > 3 else f"markets_{sys.argv[1]}_{sys.argv[2]}"
    final = os.path.join(RAW, name + ".jsonl.gz")
    if os.path.exists(final):
        print("already done:", final)
        return
    part = os.path.join(RAW, name + ".partial.jsonl")
    curf = os.path.join(RAW, name + ".cursor")
    base = ("https://gamma-api.polymarket.com/markets/keyset?closed=true&limit=100&order=closedTime"
            f"&ascending=false&volume_num_min={int(MIN_VOLUME)}")
    cur = open(curf).read().strip() if os.path.exists(curf) else None
    seen = set()
    if os.path.exists(part):
        with open(part) as f:
            for line in f:
                seen.add(json.loads(line)["id"])
    pages = 0
    with open(part, "a") as out:
        while True:
            d = get(base + (f"&after_cursor={urllib.parse.quote(cur)}" if cur else ""))
            ms = d.get("markets") or []
            pages += 1
            stop = False
            for m in ms:
                ct = parse_ts(m.get("closedTime"))
                if ct is None or ct >= d1:
                    continue
                if ct < d0:
                    stop = True
                    continue
                if m["id"] in seen:
                    continue
                seen.add(m["id"])
                r = {k: m.get(k) for k in KEEP}
                r["description"] = (m.get("description") or "")[:4000]
                evs = m.get("events") or []
                r["event"] = {k: evs[0].get(k) for k in EV_KEEP} if evs else None
                out.write(json.dumps(r, separators=(",", ":")) + "\n")
            out.flush()
            cur = d.get("next_cursor")
            if cur:
                with open(curf, "w") as cf:
                    cf.write(cur)
            if pages % 50 == 0:
                print(pages, len(seen), ms[-1]["closedTime"] if ms else None, flush=True)
            if stop or not cur or not ms:
                break
    rows = [json.loads(l) for l in open(part)]
    write_jsonl_gz(final, rows)
    os.remove(part)
    if os.path.exists(curf):
        os.remove(curf)
    print("markets", len(rows), "->", final)


if __name__ == "__main__":
    main()
