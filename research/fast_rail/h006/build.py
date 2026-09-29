"""H-006 join: football-data.co.uk rows <-> Polymarket home/draw/away match events.

Pure functions (tested offline) + loaders over data/fast_rail/h006/raw/.
Timing rules (football-data notes.txt: "Betting odds for weekend games are collected Friday
afternoons, and on Tuesday afternoons for midweek games"; exact hour not published):
collection time = Friday 18:00 UTC for Fri-Mon kickoffs, Tuesday 18:00 UTC for Tue-Thu kickoffs.
"""
from __future__ import annotations

import csv
import datetime as dt
import difflib
import glob
import gzip
import io
import json
import re
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "fast_rail" / "h006" / "raw"
UTC = dt.timezone.utc
LONDON = ZoneInfo("Europe/London")
OUTCOMES = ("H", "D", "A")


def collection_time(kickoff: dt.datetime) -> dt.datetime:
    """Football-data pre-match (PSH/PSD/PSA) collection time assumed for a kickoff (UTC)."""
    kickoff = kickoff.astimezone(UTC)
    weekday = kickoff.weekday()  # Mon=0 .. Sun=6
    back = (weekday - 4) % 7 if weekday in (4, 5, 6, 0) else (weekday - 1) % 7  # Fri or Tue
    day = (kickoff - dt.timedelta(days=back)).date()
    return dt.datetime(day.year, day.month, day.day, 18, tzinfo=UTC)


def fd_kickoff_utc(date: str, time: str) -> dt.datetime:
    """football-data Date dd/mm/yyyy + Time (UK local) -> UTC."""
    local = dt.datetime.strptime(f"{date} {time}", "%d/%m/%Y %H:%M").replace(tzinfo=LONDON)
    return local.astimezone(UTC)


_STOP = {"fc", "cf", "ac", "afc", "sc", "ssc", "as", "us", "sv", "vfb", "vfl", "tsg", "rc", "rcd", "ca",
         "ud", "cd", "sd", "de", "club", "calcio", "bv", "the", "and", "1", "04", "05", "09", "1899",
         "1846", "1848", "1907", "1910", "1913", "acf", "ogc", "losc", "stade", "olympique", "hsc", "rb",
         "real", "athletic", "atletico", "city", "united", "town", "hotspur", "wanderers", "albion"}
_ALIAS = {"man": "manchester", "utd": "united", "nott'm": "nottingham", "wolves": "wolverhampton",
          "spurs": "tottenham", "inter": "internazionale", "milan": "milan", "sociedad": "sociedad",
          "ath": "athletic", "betis": "betis", "celta": "celta", "psg": "paris", "m'gladbach": "monchengladbach",
          "gladbach": "monchengladbach", "leverkusen": "leverkusen", "koln": "koln", "fc koln": "koln",
          "st": "saint", "munich": "munchen", "munchen": "munchen", "ein": "eintracht"}


def norm_team(name: str) -> str:
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    text = text.replace(".", " ").replace("-", " ")
    words = [_ALIAS.get(w, w) for w in re.findall(r"[a-z0-9']+", text)]
    kept = [w for w in words if w not in _STOP]
    return " ".join(kept or words)


def team_sim(a: str, b: str) -> float:
    na, nb = norm_team(a), norm_team(b)
    if not na or not nb:
        return 0.0
    ta, tb = set(na.split()), set(nb.split())
    if ta & tb:
        return 1.0
    if any(x.startswith(y) or y.startswith(x) for x in ta for y in tb if min(len(x), len(y)) >= 3):
        return 0.9
    return difflib.SequenceMatcher(None, na, nb).ratio()


def load_fd() -> list[dict]:
    rows = []
    for path in sorted(RAW.glob("fd_*.csv.gz")):
        _, season, code = path.name[:-len(".csv.gz")].split("_")
        text = gzip.decompress(path.read_bytes()).decode("utf-8-sig", "replace")
        for row in csv.DictReader(io.StringIO(text)):
            if not row.get("HomeTeam") or not row.get("Time"):
                continue
            rows.append({"league": code, "season": season, "home": row["HomeTeam"], "away": row["AwayTeam"],
                         "kickoff_fd": fd_kickoff_utc(row["Date"], row["Time"]), "FTR": row["FTR"],
                         "PS": [row.get(f"PS{o}") for o in OUTCOMES],
                         "PSC": [row.get(f"PSC{o}") for o in OUTCOMES]})
    return rows


def parse_event(event: dict) -> dict | None:
    """Polymarket event -> {home, away, kickoff, tokens{H,D,A}, volume{H,D,A}, fee} or None."""
    markets = event.get("markets") or []
    tag = (event.get("slug") or "") + (event.get("title") or "").lower()
    if re.search(r"halftime|half-time|more-markets|1st-half|first-half", tag):
        return None
    if len(markets) != 3:
        return None
    draw = [m for m in markets if "draw" in (m.get("question") or "").lower()]
    if len(draw) != 1:
        return None
    title = (event.get("title") or "").split(":", 1)[-1]
    parts = re.split(r"\s+vs\.?\s+", title.strip(), maxsplit=1)
    if len(parts) != 2:
        return None
    home, away = parts[0].strip(), parts[1].strip()
    teams = [m for m in markets if m is not draw[0]]
    def label(m):
        return m.get("groupItemTitle") or re.sub(r"^Will\s+|\s+(win|beat)\b.*$", "", m.get("question") or "")
    s0 = team_sim(label(teams[0]), home) + team_sim(label(teams[1]), away)
    s1 = team_sim(label(teams[1]), home) + team_sim(label(teams[0]), away)
    if s0 == s1:
        return None
    by = {"H": teams[0] if s0 > s1 else teams[1], "D": draw[0], "A": teams[1] if s0 > s1 else teams[0]}
    tokens, volume = {}, {}
    for o, m in by.items():
        outcomes, ids = json.loads(m.get("outcomes") or "[]"), json.loads(m.get("clobTokenIds") or "[]")
        if outcomes[:1] != ["Yes"] or len(ids) != 2:
            return None
        tokens[o], volume[o] = ids[0], float(m.get("volumeNum") or m.get("volume") or 0.0)
    start = by["H"].get("gameStartTime") or event.get("startTime")
    if not start:
        return None
    kickoff = dt.datetime.fromisoformat(start.replace(" ", "T").replace("+00", "+00:00").replace("Z", "+00:00"))
    fee = by["H"].get("feeSchedule") if by["H"].get("feesEnabled") else None
    return {"slug": event["slug"], "id": event["id"], "home": home, "away": away, "kickoff_pm": kickoff,
            "tokens": tokens, "volume": volume, "fee_rate": float(fee["rate"]) if fee else 0.0}


def load_events() -> dict[str, list[dict]]:
    seen, out = set(), {}
    for path in sorted(RAW.glob("events_*.json.gz")):
        code = path.name.split("_")[1].rstrip("b")
        for event in json.loads(gzip.decompress(path.read_bytes())):
            if event["id"] in seen:
                continue
            parsed = parse_event(event)
            if parsed:
                seen.add(event["id"])
                out.setdefault(code, []).append(parsed)
    return out


def match(fd_rows: list[dict], events: dict[str, list[dict]]) -> list[dict]:
    """One Polymarket event per football-data row: same league, kickoff within 36h, best team pair."""
    used, joined = set(), []
    for row in fd_rows:
        best, best_score = None, 0.0
        for ev in events.get(row["league"], []):
            if abs((ev["kickoff_pm"] - row["kickoff_fd"]).total_seconds()) > 36 * 3600:
                continue
            sh, sa = team_sim(ev["home"], row["home"]), team_sim(ev["away"], row["away"])
            if min(sh, sa) < 0.6:
                continue
            if sh + sa > best_score:
                best, best_score = ev, sh + sa
        # a Polymarket kickoff >3h from football-data's marks a postponement: timing ambiguous, drop
        if (best and best["id"] not in used
                and abs((best["kickoff_pm"] - row["kickoff_fd"]).total_seconds()) <= 3 * 3600):
            used.add(best["id"])
            kickoff = min(best["kickoff_pm"], row["kickoff_fd"])
            joined.append({**row, **best, "kickoff": kickoff, "collection": collection_time(kickoff)})
    return joined


def matched_events() -> list[dict]:
    return [{"slug": m["slug"], "tokens": m["tokens"], "kickoff_ts": m["kickoff"].timestamp(),
             "collection_ts": m["collection"].timestamp()} for m in match(load_fd(), load_events()) if usable(m)]


def usable(m: dict) -> bool:
    """Pinnacle pre-match AND closing odds present (football-data stopped PS* mid-Jan 2026)."""
    return all(m["PS"]) and all(m["PSC"]) and m["collection"] < m["kickoff"]
