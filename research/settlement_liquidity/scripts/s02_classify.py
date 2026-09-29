"""Step 2: outcome-blind classification of the enumerated markets.

Reads data/raw/<name>.jsonl.gz (or .partial.jsonl while S1 runs) and assigns:
  excl   : exclusion code or '' (E1 up/down, E2 asset-price threshold / latency-driven, E3 non-binary/void payout)
  family : determination family used by S4 verifiers (mlb, espn:<sport>/<league>, wx_nws, wx_other, sports_other,
           esports, other)
No outcome, price or trade information is used here (outcomePrices is read only to flag E3 structure
after the fact? -> NO: E3 is decided in S6 from payout vector and reported, never used to drop losers).

Usage: python3 s02_classify.py markets_primary [--survey]
"""
import collections
import csv
import gzip
import json
import os
import re
import sys

from common import DATA, RAW, read_jsonl_gz

UPDOWN = re.compile(r"\bup or down\b", re.I)
# Asset-price threshold / range / hit markets (crypto, equities, indices, commodities, FX): latency-driven family.
ASSETS = (r"bitcoin|btc|ethereum|\beth\b|solana|\bsol\b|xrp|ripple|dogecoin|doge|bnb|cardano|hyperliquid|\bhype\b|"
          r"litecoin|chainlink|avalanche|sui\b|pepe|shiba|tron|ton\b|polkadot|crypto|s&p ?500|\bspx\b|\bspy\b|nasdaq|"
          r"\bqqq\b|dow jones|\bdji|russell 2000|nvidia|\bnvda\b|tesla|\btsla\b|apple|\baapl\b|microsoft|\bmsft\b|amazon|"
          r"\bamzn\b|meta\b|google|alphabet|\bgoog|netflix|coinbase|microstrategy|\bmstr\b|gold\b|silver\b|crude|"
          r"\boil\b|\bwti\b|brent|natural gas|eur/usd|usd/jpy|dollar index|\bdxy\b|10-year|treasury yield|vix\b|"
          r"\bspacex\b|palantir|\bpltr\b|\bamd\b|intel\b|broadcom|\bcoin\b|hood\b|robinhood")
PRICE_Q = re.compile(r"(price of|above|below|between|reach|hit|dip to|close (above|below|at)|closes? (above|below)|"
                     r"finish (above|below)|\$[0-9][0-9,\.]*[kKmM]?|all[- ]time high|\bath\b|market cap|opens? (up|down))", re.I)
ASSET_RE = re.compile(ASSETS, re.I)
WX = re.compile(r"(highest|lowest|high|low|maximum|minimum) temperature|temperature in|°[FC]|degrees", re.I)

ESPN_SERIES = {
    # gamma seriesSlug/ticker prefix -> ESPN sport/league
    "nfl": "football/nfl", "cfb": "football/college-football", "ncaaf": "football/college-football",
    "wnba": "basketball/wnba", "nba": "basketball/nba", "nhl": "hockey/nhl",
    "epl": "soccer/eng.1", "lal": "soccer/esp.1", "laliga": "soccer/esp.1", "bun": "soccer/ger.1",
    "bundesliga": "soccer/ger.1", "sea": "soccer/ita.1", "serie-a": "soccer/ita.1", "fl1": "soccer/fra.1",
    "ligue-1": "soccer/fra.1", "ucl": "soccer/uefa.champions", "uel": "soccer/uefa.europa",
    "uecl": "soccer/uefa.europa.conf", "mls": "soccer/usa.1", "ere": "soccer/ned.1", "por": "soccer/por.1",
    "efl": "soccer/eng.2", "elc": "soccer/eng.2", "tur": "soccer/tur.1", "spl": "soccer/sco.1", "bra": "soccer/bra.1",
    "arg": "soccer/arg.1", "mex": "soccer/mex.1", "lmx": "soccer/mex.1", "bel": "soccer/bel.1",
}


def classify(m):
    q = m.get("question") or ""
    ev = m.get("event") or {}
    series = (ev.get("seriesSlug") or "").lower()
    evslug = (ev.get("slug") or m.get("slug") or "").lower()
    smt = m.get("sportsMarketType") or ""
    text = q + " " + (ev.get("title") or "")
    excl = ""
    if UPDOWN.search(text) or "updown" in evslug or "up-or-down" in evslug:
        excl = "E1_UPDOWN"
    elif ASSET_RE.search(text) and PRICE_Q.search(text) and not smt:
        excl = "E2_ASSET_PRICE"
    fam = "other"
    prefix = evslug.split("-")[0] if evslug else ""
    if WX.search(text) and not smt:
        fam = "wx"
    elif series == "mlb" or prefix == "mlb":
        fam = "mlb"
    elif (series in ESPN_SERIES) or (prefix in ESPN_SERIES and (smt or ev.get("gameId"))):
        fam = "espn:" + ESPN_SERIES.get(series, ESPN_SERIES.get(prefix))
    elif smt or ev.get("gameId") or ev.get("finishedTimestamp"):
        fam = "sports_other:" + (series or prefix or "?")
    return excl, fam


def load(name):
    p = os.path.join(RAW, name + ".jsonl.gz")
    if os.path.exists(p):
        return list(read_jsonl_gz(p))
    p = os.path.join(RAW, name + ".partial.jsonl")
    return [json.loads(l) for l in open(p)]


def main():
    name = sys.argv[1]
    ms = load(name)
    rows = []
    for m in ms:
        excl, fam = classify(m)
        ev = m.get("event") or {}
        rows.append({"id": m["id"], "conditionId": m["conditionId"], "closedTime": m["closedTime"],
                     "volumeNum": round(float(m.get("volumeNum") or 0), 2), "excl": excl, "family": fam,
                     "smt": m.get("sportsMarketType") or "", "series": ev.get("seriesSlug") or "",
                     "evslug": ev.get("slug") or "", "question": (m.get("question") or "")[:140]})
    if "--survey" in sys.argv:
        print("markets", len(rows))
        c = collections.Counter(r["excl"] or "KEEP" for r in rows)
        print("exclusion", c.most_common())
        kept = [r for r in rows if not r["excl"]]
        cf = collections.Counter(r["family"].split(":")[0] if r["family"].startswith("sports_other") else r["family"] for r in kept)
        vol = collections.Counter()
        for r in kept:
            k = r["family"].split(":")[0] if r["family"].startswith("sports_other") else r["family"]
            vol[k] += r["volumeNum"]
        for k, n in cf.most_common():
            print(f"  {k:40s} n={n:7d} vol={vol[k]/1e6:9.1f}M")
        so = collections.Counter(r["family"] for r in kept if r["family"].startswith("sports_other"))
        print("sports_other top", so.most_common(40))
        oth = collections.Counter(r["evslug"].split("-")[0] for r in kept if r["family"] == "other")
        print("other evslug prefixes", oth.most_common(40))
        smt = collections.Counter((r["family"].split(":")[0], r["smt"]) for r in kept if r["smt"])
        print("sportsMarketType", smt.most_common(60))
        return
    out = os.path.join(DATA, f"cohort_{name.replace('markets_', '')}.csv.gz")
    with gzip.open(out, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out, len(rows))


if __name__ == "__main__":
    main()
