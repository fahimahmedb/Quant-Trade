"""Step 8: READ-ONLY live queue monitor for post-final, pre-resolution markets. Places no orders.

Loop:
  - every 5 min: index open Polymarket sports events (gamma, tag Sports) that started in the last 10 h;
  - every 60 s : poll authoritative finals (ESPN scoreboards: soccer/all, NFL, NCAAF, WNBA, NHL; MLB statsapi);
                 a game seen final for the first time gets t_seen_final = poll time (what a newcomer observes);
                 matched open events (kickoff ±20 min, team similarity) are added to tracking;
  - every 20 s : public CLOB POST /books for every tracked token; stores levels at >=0.99 bids / <=0.01 asks
                 plus best bid/ask, per token;
  - a market leaves tracking when gamma reports it closed, the book disappears, or after 12 h.
Outputs (append-only, resumable): data/raw/live/books.jsonl, data/raw/live/tracked.jsonl, data/raw/live/finals.jsonl
Usage: python3 s08_live_queue_monitor.py <hours_to_run>
"""
import datetime as dt
import json
import os
import re
import sys
import time

from common import RAW, get, parse_ts, post
from s04b_espn import sim

LIVE = os.path.join(RAW, "live")
os.makedirs(LIVE, exist_ok=True)
FEEDS = [("soccer/all", ""), ("football/nfl", ""), ("football/college-football", "&groups=80"),
         ("football/college-football", "&groups=81"), ("basketball/wnba", ""), ("hockey/nhl", "")]


def jl(name, rec):
    with open(os.path.join(LIVE, name), "a") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")


def open_sports_events(now):
    out = []
    smin = dt.datetime.fromtimestamp(now - 10 * 3600, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    smax = dt.datetime.fromtimestamp(now + 600, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for off in range(0, 3000, 100):
        try:
            d = get(f"https://gamma-api.polymarket.com/events?closed=false&tag_id=1&limit=100&offset={off}"
                    f"&start_time_min={smin}&start_time_max={smax}")  # game start (start_date_* is event creation)
        except Exception:
            break
        out += d
        if len(d) < 100:
            break
    evs = []
    for e in out:
        st = parse_ts(e.get("startTime"))
        if st is None:
            continue
        mk = []
        for m in e.get("markets", []) or []:
            if m.get("closed"):
                continue
            try:
                toks = json.loads(m["clobTokenIds"])
                outs = json.loads(m["outcomes"])
            except Exception:
                continue
            mk.append({"conditionId": m["conditionId"], "tokens": toks, "outcomes": outs, "q": m.get("question"),
                       "smt": m.get("sportsMarketType"), "id": m.get("id")})
        if mk:
            evs.append({"slug": e["slug"], "title": e.get("title") or "", "start": st, "markets": mk})
    return evs


def finals(now):
    res = []
    days = {dt.datetime.fromtimestamp(now - h * 3600, dt.timezone.utc).strftime("%Y%m%d") for h in (0, 12)}
    for path, extra in FEEDS:
        for day in days:
            try:
                d = get(f"https://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard?dates={day}&limit=1000{extra}")
            except Exception:
                continue
            for e in d.get("events", []):
                st = e["status"]["type"]
                if not st.get("completed"):
                    continue
                comp = e["competitions"][0]
                teams = [[c["team"].get(k) for k in ("displayName", "shortDisplayName", "name", "location", "abbreviation")]
                         for c in comp["competitors"]]
                res.append({"key": "espn:" + e["id"], "start": parse_ts(e["date"]), "teams": teams, "status": st.get("name"),
                            "name": e["name"]})
    for day in {dt.datetime.fromtimestamp(now - h * 3600, dt.timezone.utc).strftime("%Y-%m-%d") for h in (0, 12)}:
        try:
            s = get(f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={day}")
        except Exception:
            continue
        for dd in s.get("dates", []):
            for g in dd["games"]:
                if g["status"].get("codedGameState") != "F":
                    continue
                res.append({"key": f"mlb:{g['gamePk']}", "start": parse_ts(g["gameDate"]), "status": "Final",
                            "teams": [[g["teams"]["away"]["team"]["name"]], [g["teams"]["home"]["team"]["name"]]],
                            "name": g["teams"]["away"]["team"]["name"] + " at " + g["teams"]["home"]["team"]["name"]})
    return res


def match(fin, evs):
    out = []
    for e in evs:
        if abs(e["start"] - fin["start"]) > 1200:
            continue
        parts = re.split(r"\s+(?:vs\.?|v\.?|@|at)\s+", e["title"], maxsplit=1, flags=re.I)
        if len(parts) != 2:
            continue
        a, b = re.sub(r"^.*?:\s*", "", parts[0]), re.sub(r"\s*[-–(].*$", "", parts[1])
        t0, t1 = fin["teams"][0], fin["teams"][1]
        s = max(sim(t0, a) + sim(t1, b), sim(t0, b) + sim(t1, a))
        if s >= 1.5:
            out.append(e)
    return out


def main():
    hours = float(sys.argv[1]) if len(sys.argv) > 1 else 8
    t_end = time.time() + hours * 3600
    seen_final = {}
    tracked = {}  # conditionId -> meta
    evs, t_evs, t_fin, t_chk = [], 0, 0, time.time()
    gone = {}
    resumed = False
    if os.path.exists(os.path.join(LIVE, "finals.jsonl")):
        for l in open(os.path.join(LIVE, "finals.jsonl")):
            r = json.loads(l)
            seen_final[r["key"]] = r
            resumed = True
    while time.time() < t_end:
        now = time.time()
        if now - t_evs > 300:
            try:
                evs = open_sports_events(now)
            except Exception as ex:
                print("events err", ex, flush=True)
            t_evs = now
        if now - t_fin > 60:
            try:
                fs = finals(now)
            except Exception as ex:
                fs = []
                print("finals err", ex, flush=True)
            for f in fs:
                if f["key"] in seen_final:
                    continue
                f["t_seen_final"] = now
                f["first_poll"] = t_fin == 0 and not resumed  # finals already present at first start: true final time unknown
                seen_final[f["key"]] = f
                jl("finals.jsonl", f)
                if f["first_poll"]:
                    continue  # unknown true final time -> not used for t_p; still tracked for depth only
            for f in seen_final.values():
                for e in match(f, evs):
                    for m in e["markets"]:
                        if m["conditionId"] in tracked:
                            continue
                        meta = {**m, "event": e["slug"], "final_key": f["key"], "t_seen_final": f["t_seen_final"],
                                "first_poll": f.get("first_poll", False), "t_track": now}
                        tracked[m["conditionId"]] = meta
                        jl("tracked.jsonl", meta)
            t_fin = now
        if tracked:
            toks = [(cid, i, t) for cid, m in tracked.items() for i, t in enumerate(m["tokens"])]
            for k in range(0, len(toks), 60):
                batch = toks[k:k + 60]
                try:
                    bs = post("https://clob.polymarket.com/books", [{"token_id": t} for _, _, t in batch])
                except Exception as ex:
                    print("books err", ex, flush=True)
                    continue
                bym = {b["asset_id"]: b for b in bs if isinstance(b, dict) and b.get("asset_id")}
                ts = time.time()
                for cid, i, t in batch:
                    b = bym.get(t)
                    if not b:
                        jl("books.jsonl", {"ts": ts, "c": cid, "i": i, "gone": 1})
                        gone[cid] = gone.get(cid, 0) + 1
                        continue
                    bids = [(float(x["price"]), float(x["size"])) for x in b.get("bids", [])]
                    asks = [(float(x["price"]), float(x["size"])) for x in b.get("asks", [])]
                    jl("books.jsonl", {"ts": ts, "c": cid, "i": i, "bt": b.get("timestamp"), "tick": b.get("tick_size"),
                                       "bb": max(bids)[0] if bids else None, "ba": min(asks)[0] if asks else None,
                                       "hb": [x for x in bids if x[0] >= 0.99], "la": [x for x in asks if x[0] <= 0.01],
                                       "ltp": b.get("last_trade_price")})
        if now - t_chk > 300 and tracked:
            cids = list(tracked)
            for k in range(0, len(cids), 40):
                chunk = cids[k:k + 40]
                try:
                    g = get("https://gamma-api.polymarket.com/markets?closed=true&limit=100&" + "&".join(f"condition_ids={c}" for c in chunk))
                except Exception:
                    continue
                for mm in g or []:
                    cid = mm.get("conditionId")
                    if cid in tracked and mm.get("closed"):
                        jl("tracked.jsonl", {"conditionId": cid, "closed_seen": now, "closedTime": mm.get("closedTime")})
                        tracked.pop(cid)
            for cid in list(tracked):
                if now - tracked[cid]["t_track"] > 12 * 3600 or gone.get(cid, 0) >= 6:
                    tracked.pop(cid)
            t_chk = now
        print(time.strftime("%H:%M:%S"), "tracked", len(tracked), "finals", len(seen_final), flush=True)
        time.sleep(max(1, 20 - (time.time() - now)))


if __name__ == "__main__":
    main()
