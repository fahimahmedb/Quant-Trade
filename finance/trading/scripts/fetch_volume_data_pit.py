"""Récupération du volume quotidien pour l'univers point-in-time (214
tickers de `data/pead/prices_pit/*.json`, cf. cycle #163), jamais
récupéré jusqu'ici -- même API Yahoo déjà validée
(`fetch_ndx100_pit_universe.py`, `fetch_volume_data.py`). Script séparé
pour ne jamais modifier les données de prix PIT déjà committées. PREREG :
`PREREG_volume_candidates_pit_universe.md`, committé avant ce script.
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
VOLUME_PIT_DIR = ROOT / "data" / "pead" / "volume_pit"
VOLUME_PIT_DIR.mkdir(parents=True, exist_ok=True)

PERIOD1 = 0            # tout l'historique disponible (identique a fetch_ndx100_pit_universe.py)
PERIOD2 = 1785200000   # ~28/07/2026
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
    tickers = sorted(p.stem for p in PRICES_PIT_DIR.glob("*.json"))
    n_ok, n_fail = 0, 0
    for i, ticker in enumerate(tickers):
        out_path = VOLUME_PIT_DIR / f"{ticker}.json"
        if out_path.exists():
            continue
        y_ticker = ticker.replace(".", "-")
        url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{y_ticker}"
               f"?period1={PERIOD1}&period2={PERIOD2}&interval=1d")
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
            print(f"[volume_pit] ÉCHEC {ticker}: {e}", flush=True)
        if (i + 1) % 20 == 0 or i == len(tickers) - 1:
            print(f"[volume_pit] {i+1}/{len(tickers)} tickers traités ({n_ok} OK, {n_fail} échec)", flush=True)
        time.sleep(SLEEP_S)
    print(f"Terminé : {n_ok} OK, {n_fail} échec sur {len(tickers)} tickers")


if __name__ == "__main__":
    main()
