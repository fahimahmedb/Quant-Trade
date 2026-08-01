"""Récupération des prix de TOUS les tickers ayant appartenu au NDX-100
entre 2015 et 2026 (214 symboles), et pas seulement des 103 membres
actuels — condition nécessaire pour reconstruire l'univers point-in-time
sans biais du survivant.

Cycle #163 du backlog non-ML, spécifié dans
`PREREG_leaders_index52w_high_overlay_pit_universe.md`, committé AVANT ce
script et avant tout fetch.

Écrit dans un dossier NOUVEAU et SÉPARÉ (`data/pead/prices_pit/`) : les
dossiers `data/pead/prices/` (52 cycles historiques) et
`data/pead/prices_extended/` (cycle #162) ne sont JAMAIS modifiés
(Règle 6).

Checkpointing : ne re-télécharge jamais un ticker déjà présent, même
convention que `pead_fetch_data.py` et `fetch_ndx100_extended_history.py`.
Les échecs (titres retirés de la cote dont Yahoo n'a plus la série) sont
écrits tels quels avec un champ `error` et **comptés dans le rapport
final** : ils constituent le biais résiduel du cycle, à quantifier et non
à masquer.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ndx100_membership import all_tickers_ever  # noqa: E402

OUT_DIR = ROOT / "data" / "pead" / "prices_pit"
OUT_DIR.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SLEEP_S = 0.4
PERIOD1 = 0            # tout l'historique disponible
PERIOD2 = 1785200000   # ~28/07/2026


def http_get_json(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            if attempt == retries - 1:
                return None
            time.sleep(2 * (attempt + 1))
    return None


def fetch_ticker(ticker: str):
    url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={PERIOD1}&period2={PERIOD2}&interval=1d")
    data = http_get_json(url)
    if data is None:
        return {"error": "http_get_json a echoue apres retries"}
    try:
        result = data["chart"]["result"][0]
        return {"ts": result["timestamp"],
                "close": result["indicators"]["quote"][0]["close"]}
    except (KeyError, IndexError, TypeError):
        return {"error": f"reponse inattendue : {json.dumps(data)[:200]}"}


def main():
    tickers = sorted(all_tickers_ever())
    done = {p.stem for p in OUT_DIR.glob("*.json")}
    todo = [t for t in tickers if t not in done]
    print(f"{len(tickers)} tickers au total, {len(done)} deja recuperes, {len(todo)} restants",
          flush=True)
    for i, t in enumerate(todo):
        payload = fetch_ticker(t)
        (OUT_DIR / f"{t}.json").write_text(json.dumps(payload))
        n = len(payload.get("ts", []) or [])
        status = "OK" if "error" not in payload else "ERREUR"
        print(f"[{i+1}/{len(todo)}] {t}: {n} points -- {status}", flush=True)
        time.sleep(SLEEP_S)

    ok, err = [], []
    for t in tickers:
        p = OUT_DIR / f"{t}.json"
        payload = json.loads(p.read_text()) if p.exists() else {"error": "absent"}
        (err if "error" in payload else ok).append(t)
    print(f"\nTermine. {len(ok)} series recuperees, {len(err)} echecs.")
    if err:
        print("Echecs : " + ", ".join(err))


if __name__ == "__main__":
    main()
