"""Récupération du volume quotidien (nouvelle catégorie de données, jamais
utilisée dans ce backlog) pour les tickers NDX-100 déjà présents dans
`data/pead/prices/*.json`, via la même API Yahoo Finance déjà validée
(`pead_fetch_data.py::fetch_prices`, champ `volume` jamais extrait
jusqu'ici). Script séparé pour ne jamais modifier le fetch de prix
existant. PREREG : `PREREG_momentum_turnover_doublesort.md`, committé
avant ce script.
"""
import json
import time
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRICES_DIR = ROOT / "data" / "pead" / "prices"
VOLUME_DIR = ROOT / "data" / "pead" / "volume"
VOLUME_DIR.mkdir(parents=True, exist_ok=True)

PRICE_PERIOD1 = date(2021, 1, 1)
PRICE_PERIOD2 = date(2026, 8, 15)
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


def main():
    tickers = sorted(p.stem for p in PRICES_DIR.glob("*.json"))
    period1 = int(time.mktime(PRICE_PERIOD1.timetuple()))
    period2 = int(time.mktime(PRICE_PERIOD2.timetuple()))
    n_ok, n_fail = 0, 0
    for i, ticker in enumerate(tickers):
        out_path = VOLUME_DIR / f"{ticker}.json"
        if out_path.exists():
            continue
        y_ticker = ticker.replace(".", "-")
        url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{y_ticker}"
               f"?period1={period1}&period2={period2}&interval=1d")
        payload = http_get_json(url)
        try:
            result = payload["chart"]["result"][0]
            ts = result["timestamp"]
            volume = result["indicators"]["quote"][0]["volume"]
            out_path.write_text(json.dumps({"ts": ts, "volume": volume}))
            n_ok += 1
        except Exception as e:
            out_path.write_text(json.dumps({"error": str(e)}))
            n_fail += 1
            print(f"[volume] ÉCHEC {ticker}: {e}", flush=True)
        if (i + 1) % 20 == 0 or i == len(tickers) - 1:
            print(f"[volume] {i+1}/{len(tickers)} tickers traités ({n_ok} OK, {n_fail} échec)", flush=True)
        time.sleep(SLEEP_S)
    print(f"Terminé : {n_ok} OK, {n_fail} échec sur {len(tickers)} tickers")


if __name__ == "__main__":
    main()
