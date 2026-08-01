"""Récupération de l'historique COMPLET disponible (pas de borne à 2021,
contrairement à `pead_fetch_data.py` qui bornait à `PRICE_PERIOD1 =
date(2021, 1, 1)` pour les besoins du protocole PEAD) pour les ~100
tickers NDX-100 déjà identifiés (`data/pead/ndx100_constituents.json`).

Motivation (cycle #162 du backlog non-ML, PREREG_leaders_index52w_high_
overlay_extended_history.md) : le #38 (Leaders 52-semaines + overlay
52w-high indice) a obtenu au cycle #161 le meilleur score de batterie
Règle 9 jamais atteint (4/5, DSR=0,730), borné par un échantillon de
seulement ~4,5 ans utilisables (2022-2026, après le warm-up de 252j).
Étendre l'historique teste si le DSR grimpe avec plus de données (edge
réel borné par la puissance statistique) ou se dégrade (fenêtre 2022-2026
favorable par chance).

Écrit dans un dossier SÉPARÉ (`data/pead/prices_extended/`) pour ne
JAMAIS modifier `data/pead/prices/` déjà utilisé par les 161 cycles
précédents (traçabilité, Règle 6 du protocole anti-snooping).

Checkpointing : reprend exactement où il s'est arrêté (ne re-télécharge
jamais un ticker déjà présent), même convention que `pead_fetch_data.py`.
"""
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # finance/trading
CONSTITUENTS_PATH = ROOT / "data" / "pead" / "ndx100_constituents.json"
OUT_DIR = ROOT / "data" / "pead" / "prices_extended"
OUT_DIR.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SLEEP_S = 0.5
# period1=0 -- Yahoo renvoie tout l'historique disponible depuis l'IPO
# (ou le début de la cotation), pas de borne artificielle imposée ici.
PERIOD1 = 0
PERIOD2 = 1785200000  # ~28/07/2026, marge suffisante


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


def fetch_ticker(ticker: str):
    url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={PERIOD1}&period2={PERIOD2}&interval=1d")
    data = http_get_json(url)
    if data is None:
        return {"error": "http_get_json a echoue apres retries"}
    try:
        result = data["chart"]["result"][0]
        ts = result["timestamp"]
        close = result["indicators"]["quote"][0]["close"]
        return {"ts": ts, "close": close}
    except (KeyError, IndexError, TypeError):
        return {"error": f"reponse inattendue : {json.dumps(data)[:300]}"}


def main():
    tickers = json.loads(CONSTITUENTS_PATH.read_text())
    done = {p.stem for p in OUT_DIR.glob("*.json")}
    todo = [t for t in tickers if t not in done]
    print(f"{len(done)} deja recuperes, {len(todo)} restants sur {len(tickers)}")
    for i, t in enumerate(todo):
        payload = fetch_ticker(t)
        out = OUT_DIR / f"{t}.json"
        out.write_text(json.dumps(payload))
        n = len(payload.get("ts", []))
        status = "OK" if "error" not in payload else f"ERREUR: {payload['error'][:80]}"
        print(f"[{i+1}/{len(todo)}] {t}: {n} points -- {status}", flush=True)
        time.sleep(SLEEP_S)
    print("Termine.")


if __name__ == "__main__":
    main()
