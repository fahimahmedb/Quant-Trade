"""Récupération des données PEAD (résultats trimestriels + prix), conforme
au pré-enregistrement `finance/trading/PEAD_PREREGISTRATION.md` (univers,
période, source figés AVANT ce script).

Deux sources publiques gratuites, testées manuellement avant d'écrire ce
script (aucune n'exige de clé API) :
- api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD : surprise de
  résultats par jour, historique disponible depuis au moins 2015.
- query2.finance.yahoo.com (chart API) : prix quotidiens par titre, déjà
  utilisé et validé dans ce projet (fetch_and_quantify_putwrite.py).

Checkpointing : ce script est concu pour tourner en tache de fond sans
supervision ("mode auto") et pour reprendre exactement ou il s'est arrete
en cas d'interruption -- il ne re-interroge jamais un jour ou un ticker
deja recupere.
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # finance/trading
DATA_DIR = ROOT / "data" / "pead"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONSTITUENTS_PATH = DATA_DIR / "ndx100_constituents.json"
EVENTS_PATH = DATA_DIR / "earnings_events.json"
EVENTS_PROGRESS_PATH = DATA_DIR / "earnings_fetch_progress.json"
PRICES_DIR = DATA_DIR / "prices"
PRICES_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = date(2021, 7, 1)
END_DATE = date(2026, 7, 27)
PRICE_PERIOD1 = date(2021, 1, 1)   # marge avant pour le split design
PRICE_PERIOD2 = date(2026, 8, 15)  # marge apres pour couvrir H=60j de la derniere annonce

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SLEEP_S = 0.35


def http_get_json(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if attempt == retries - 1:
                return None
            time.sleep(2 * (attempt + 1))
    return None


def fetch_constituents() -> list:
    if CONSTITUENTS_PATH.exists():
        return json.loads(CONSTITUENTS_PATH.read_text())
    payload = http_get_json("https://api.nasdaq.com/api/quote/list-type/nasdaq100")
    rows = payload["data"]["data"]["rows"]
    tickers = sorted({r["symbol"] for r in rows if r.get("symbol")})
    CONSTITUENTS_PATH.write_text(json.dumps(tickers, indent=2))
    return tickers


def daterange_weekdays(d0: date, d1: date):
    d = d0
    while d <= d1:
        if d.weekday() < 5:  # lun-ven seulement (pas de resultats publies le week-end)
            yield d
        d += timedelta(days=1)


def fetch_earnings_events(universe: set) -> list:
    events = json.loads(EVENTS_PATH.read_text()) if EVENTS_PATH.exists() else []
    done_dates = set(json.loads(EVENTS_PROGRESS_PATH.read_text())) if EVENTS_PROGRESS_PATH.exists() else set()

    all_days = list(daterange_weekdays(START_DATE, END_DATE))
    remaining = [d for d in all_days if d.isoformat() not in done_dates]
    print(f"[earnings] {len(done_dates)}/{len(all_days)} jours déjà récupérés, {len(remaining)} restants",
          flush=True)

    for i, d in enumerate(remaining):
        ds = d.isoformat()
        payload = http_get_json(f"https://api.nasdaq.com/api/calendar/earnings?date={ds}")
        rows = ((payload or {}).get("data") or {}).get("rows") or []
        for r in rows:
            sym = r.get("symbol")
            if sym not in universe:
                continue
            surprise_raw = r.get("surprise")
            try:
                surprise = float(surprise_raw)
            except (TypeError, ValueError):
                continue  # surprise manquante (ex: perte -> % non défini) : événement exclu, pas imputé
            events.append({"date": ds, "symbol": sym, "surprise_pct": surprise})
        done_dates.add(ds)

        if (i + 1) % 25 == 0 or i == len(remaining) - 1:
            EVENTS_PATH.write_text(json.dumps(events, indent=2))
            EVENTS_PROGRESS_PATH.write_text(json.dumps(sorted(done_dates)))
            print(f"[earnings] {i+1}/{len(remaining)} jours traités, {len(events)} événements NDX-100 cumulés",
                  flush=True)
        time.sleep(SLEEP_S)

    EVENTS_PATH.write_text(json.dumps(events, indent=2))
    EVENTS_PROGRESS_PATH.write_text(json.dumps(sorted(done_dates)))
    return events


def fetch_prices(tickers: list):
    period1 = int(time.mktime(PRICE_PERIOD1.timetuple()))
    period2 = int(time.mktime(PRICE_PERIOD2.timetuple()))
    for i, ticker in enumerate(tickers):
        out_path = PRICES_DIR / f"{ticker}.json"
        if out_path.exists():
            continue
        y_ticker = ticker.replace(".", "-")  # convention Yahoo pour les classes d'actions (ex: BRK.B -> BRK-B)
        url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{y_ticker}"
               f"?period1={period1}&period2={period2}&interval=1d")
        payload = http_get_json(url)
        try:
            result = payload["chart"]["result"][0]
            if result["meta"].get("dataGranularity") != "1d":
                raise ValueError("granularité inattendue")
            ts = result["timestamp"]
            close = result["indicators"]["quote"][0]["close"]
            out_path.write_text(json.dumps({"ts": ts, "close": close}))
        except Exception as e:
            out_path.write_text(json.dumps({"error": str(e)}))
            print(f"[prices] ÉCHEC {ticker}: {e}", flush=True)
        if (i + 1) % 10 == 0 or i == len(tickers) - 1:
            print(f"[prices] {i+1}/{len(tickers)} tickers traités", flush=True)
        time.sleep(SLEEP_S)


def main():
    tickers = fetch_constituents()
    print(f"Univers NDX-100 : {len(tickers)} tickers", flush=True)
    universe = set(tickers)

    events = fetch_earnings_events(universe)
    print(f"Total événements résultats NDX-100 récupérés : {len(events)}", flush=True)

    event_tickers = sorted({e["symbol"] for e in events})
    print(f"Tickers avec au moins 1 événement : {len(event_tickers)}", flush=True)
    fetch_prices(event_tickers)

    print("Récupération terminée.", flush=True)


if __name__ == "__main__":
    main()
