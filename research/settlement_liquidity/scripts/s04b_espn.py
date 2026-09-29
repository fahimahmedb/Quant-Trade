"""Step 4b: ESPN authoritative game timelines (wall-clock of terminal plays) + Polymarket event matching.

ESPN public site API (site.api.espn.com) publishes play-by-play with `wallclock` timestamps:
  football: drives[].plays[] types 'End of Game'(66), 'End of Half'(65), 'End Period'(2)
  soccer  : keyEvents[] types 'end-regular-time', 'halftime', 'end-extra-time', shootout ends
  basketball/hockey: plays[] with wallclock; last play of final period
Polymarket events (gamma, from S1 file) are matched to ESPN events by kickoff (|dt| <= 20 min) and
team-name similarity. Unmatched events are DETERMINATION_UNVERIFIABLE for this family.

Usage: python3 s04b_espn.py markets_primary 2026-08-28 2026-09-29
Outputs: data/espn_events_<tag>.csv.gz, data/pm_espn_map_<tag>.csv.gz  (caches in data/raw/espn/)
"""
import collections
import concurrent.futures as cf
import csv
import datetime as dt
import gzip
import json
import os
import re
import sys
import unicodedata

from common import DATA, RAW, get, parse_ts
from s02_classify import load

CACHE = os.path.join(RAW, "espn")
os.makedirs(CACHE, exist_ok=True)
FEEDS = [("football/nfl", ""), ("football/college-football", "&groups=80"), ("football/college-football", "&groups=81"),
         ("basketball/wnba", ""), ("hockey/nhl", ""), ("soccer/all", "")]
NON_ESPN = re.compile(r"^(atp|wta|itf|counter-strike|league-of-legends|dota-2|valorant|ufc|f1|rainbow-six|pdcdarts|"
                      r"international-cricket|cricket|npb|kbo|khl|golf|pga|lpga|nascar|boxing|cod|overwatch|"
                      r"starcraft|mobile-legends|honor-of-kings|rocket-league|chess|table-tennis|volleyball)")
STOP = {"fc", "cf", "sc", "afc", "cd", "ud", "club", "de", "the", "ac", "as", "sd", "ca", "cp", "fk", "sk", "if", "bk",
        "vs", "v", "and", "united", "city", "real", "sporting", "athletic", "atletico", "deportivo", "university",
        "state", "st", "women", "w", "u21", "u23", "1", "2"}


def norm_tokens(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t]
    core = [t for t in toks if t not in STOP]
    return set(core or toks)


def sim(a_names, b):
    bt = norm_tokens(b)
    best = 0.0
    for a in a_names:
        at = norm_tokens(a)
        if not at or not bt:
            continue
        inter = len(at & bt)
        best = max(best, inter / min(len(at), len(bt)))
    return best


def scoreboard(path, extra, day):
    fn = os.path.join(CACHE, f"sb_{path.replace('/', '_')}{extra.replace('&', '_').replace('=', '')}_{day}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    d = get(f"https://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard?dates={day}&limit=1000{extra}")
    evs = []
    for e in d.get("events", []):
        comp = e["competitions"][0]
        teams = []
        for c in comp["competitors"]:
            t = c["team"]
            teams.append({"ha": c.get("homeAway"), "names": [t.get("displayName"), t.get("shortDisplayName"),
                          t.get("name"), t.get("location"), t.get("abbreviation")]})
        league = e["uid"].split("~")[1] if "~" in e["uid"] else ""
        evs.append({"id": e["id"], "path": path, "league": league, "date": e["date"], "name": e["name"],
                    "status": e["status"]["type"]["name"], "teams": teams})
    json.dump(evs, open(fn, "w"))
    return evs


def timeline(path, eid):
    fn = os.path.join(CACHE, f"sum_{eid}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    sp = "soccer/all" if path.startswith("soccer") else path
    d = get(f"https://site.api.espn.com/apis/site/v2/sports/{sp}/summary?event={eid}")
    comp = d["header"]["competitions"][0]
    st = comp.get("status", {}).get("type", {})
    rec = {"id": eid, "path": path, "status": st.get("name"), "completed": st.get("completed"),
           "competitors": [{"ha": c.get("homeAway"), "name": c["team"].get("displayName"), "score": c.get("score"),
                            "winner": c.get("winner"),
                            "lines": [l.get("displayValue") for l in c.get("linescores", [])]}
                           for c in comp["competitors"]],
           "events": []}
    ev = rec["events"]
    if "drives" in d:
        for dr in (d["drives"] or {}).get("previous", []):
            for p in dr.get("plays", []):
                ev.append([p["type"].get("text"), (p.get("period") or {}).get("number"), p.get("wallclock")])
    for k in d.get("keyEvents", []) or []:
        ev.append([(k.get("type") or {}).get("type"), (k.get("period") or {}).get("number"), k.get("wallclock")])
    for p in d.get("plays", []) or []:
        ev.append([(p.get("type") or {}).get("text"), (p.get("period") or {}).get("number"), p.get("wallclock")])
    # soccer: detect statistics for corners (for outcome mapping later)
    try:
        for t in d["boxscore"]["teams"]:
            for s in t.get("statistics", []):
                if s.get("name") in ("wonCorners", "totalGoals"):
                    rec.setdefault("stats", {}).setdefault(t["team"]["displayName"], {})[s["name"]] = s.get("displayValue")
    except Exception:
        pass
    json.dump(rec, open(fn, "w"))
    return rec


def derive(rec):
    """Terminal wall-clock timestamps from ESPN timeline."""
    evs = [(t or "", p, parse_ts(w)) for t, p, w in rec["events"] if w]
    out = {"t_final": None, "t_half": None, "t_q1": None, "t_last": None, "t_end_all": None, "method": ""}
    if not evs:
        return out
    out["t_last"] = max(w for _, _, w in evs)
    tl = lambda s: [w for t, _, w in evs if t.lower() == s]
    if rec["path"].startswith("football"):
        eg = tl("end of game")
        out["t_final"] = max(eg) if eg else None
        out["method"] = "end_of_game" if eg else ""
        eh = tl("end of half")
        out["t_half"] = min(eh) if eh else None
        q1 = [w for t, p, w in evs if t.lower() == "end period" and p == 1]
        out["t_q1"] = min(q1) if q1 else None
    elif rec["path"].startswith("soccer"):
        er = tl("end-regular-time")
        out["t_final"] = max(er) if er else None
        out["method"] = "end_regular_time" if er else ""
        ht = tl("halftime")
        out["t_half"] = min(ht) if ht else None
        term = [w for t, _, w in evs if (t.lower().startswith("end-") and t.lower() != "end-delay") or "shootout" in t.lower()]
        out["t_end_all"] = max(term) if term else None
    else:  # basketball / hockey: last play of the game
        eg = [w for t, _, w in evs if t.lower() in ("end game", "end of game", "game end")]
        out["t_final"] = max(eg) if eg else None
        out["method"] = "end_game" if eg else ""
        eh = [w for t, p, w in evs if t.lower() in ("end period", "end of period") and p == 2]
        out["t_half"] = min(eh) if eh else None
    return out


def main():
    name, d0, d1 = sys.argv[1], dt.date.fromisoformat(sys.argv[2]), dt.date.fromisoformat(sys.argv[3])
    tag = name.replace("markets_", "")
    from s02_classify import classify
    ms = load(name)
    pm_events = {}
    for m in ms:
        excl, fam = classify(m)
        if excl or not (fam.startswith("espn:") or fam.startswith("sports_other:")):
            continue
        if fam.startswith("sports_other:") and NON_ESPN.match(fam.split(":", 1)[1]):
            continue
        ev = m.get("event") or {}
        k = ev.get("id")
        if not k or k in pm_events:
            continue
        start = parse_ts(m.get("gameStartTime") or ev.get("startTime"))
        pm_events[k] = {"pm_event": k, "title": ev.get("title") or m.get("question"), "start": start, "family": fam,
                        "slug": ev.get("slug")}
    print("pm events to match", len(pm_events), flush=True)
    days = []
    day = d0
    while day <= d1:
        days.append(day.strftime("%Y%m%d"))
        day += dt.timedelta(days=1)
    espn = {}
    jobs = [(p, x, dday) for p, x in FEEDS for dday in days]
    with cf.ThreadPoolExecutor(8) as ex:
        for evs in ex.map(lambda j: scoreboard(*j), jobs):
            for e in evs:
                espn[e["id"]] = e
    print("espn events", len(espn), flush=True)
    by_hour = collections.defaultdict(list)
    for e in espn.values():
        t = parse_ts(e["date"])
        e["t"] = t
        by_hour[int(t // 3600)].append(e)
    matches = []
    for k, pe in pm_events.items():
        if pe["start"] is None:
            continue
        title = pe["title"] or ""
        parts = re.split(r"\s+(?:vs\.?|v\.?|@|at)\s+", title, maxsplit=1, flags=re.I)
        if len(parts) != 2:
            continue
        a, b = parts[0], re.sub(r"\s*[-–(].*$", "", parts[1])
        a = re.sub(r"^.*?:\s*", "", a)
        best = None
        h = int(pe["start"] // 3600)
        for hh in (h - 1, h, h + 1):
            for e in by_hour.get(hh, []):
                if abs(e["t"] - pe["start"]) > 1200:
                    continue
                t0, t1 = e["teams"][0]["names"], e["teams"][1]["names"]
                s = max(sim(t0, a) + sim(t1, b), sim(t0, b) + sim(t1, a))
                if best is None or s > best[0]:
                    best = (s, e)
        if best and best[0] >= 1.5:
            matches.append((k, best[1], best[0]))
    print("matched", len(matches), flush=True)
    uniq = {e["id"]: e for _, e, _ in matches}
    with cf.ThreadPoolExecutor(8) as ex:
        recs = dict(zip(uniq, ex.map(lambda e: timeline(e["path"], e["id"]), uniq.values())))
    rows = []
    for eid, rec in recs.items():
        dv = derive(rec)
        c = {x["ha"]: x for x in rec["competitors"]}
        rows.append({"espn_id": eid, "path": rec["path"], "league": uniq[eid]["league"], "name": uniq[eid]["name"],
                     "status": rec["status"], "completed": rec["completed"],
                     "home": (c.get("home") or {}).get("name"), "away": (c.get("away") or {}).get("name"),
                     "home_score": (c.get("home") or {}).get("score"), "away_score": (c.get("away") or {}).get("score"),
                     "home_lines": json.dumps((c.get("home") or {}).get("lines")),
                     "away_lines": json.dumps((c.get("away") or {}).get("lines")),
                     "stats": json.dumps(rec.get("stats")), **dv})
    out = os.path.join(DATA, f"espn_events_{tag}.csv.gz")
    with gzip.open(out, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    out2 = os.path.join(DATA, f"pm_espn_map_{tag}.csv.gz")
    with gzip.open(out2, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pm_event", "espn_id", "match_score", "pm_title", "espn_name", "pm_start", "espn_start"])
        for k, e, s in matches:
            w.writerow([k, e["id"], round(s, 3), pm_events[k]["title"], e["name"], pm_events[k]["start"], e["t"]])
    print("wrote", out, len(rows), out2, len(matches))
    print("method counts", collections.Counter(r["method"] or "NONE" for r in rows))


if __name__ == "__main__":
    main()
