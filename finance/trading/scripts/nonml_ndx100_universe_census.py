"""Recensement de l'univers NDX-100 disponible par date (cycle #163).

**Ce script ne calcule AUCUNE performance de stratégie** — uniquement la
DISPONIBILITÉ des données de prix (combien de titres de la liste NDX-100
de 2026 ont assez d'historique pour être éligibles à une date donnée).
Il est exécuté et committé AVANT le pré-enregistrement du cycle #163
parce que son unique rôle est de JUSTIFIER CHIFFRÉEMENT le choix de la
borne de début de fenêtre (Règle 6 : traçabilité ; Règle 1 : le PREREG
doit fixer une borne justifiée, pas devinée). Aucun rendement, aucun
Sharpe, aucun signal n'est calculé ici — il est donc impossible de
« choisir la borne qui donne le meilleur résultat ».

Critère d'éligibilité repris À L'IDENTIQUE du mécanisme déjà committé
(`nonml_leaders_index52w_high_overlay_backtest.build_weights`) : un titre
est éligible à la date D s'il dispose de LOOKBACK=252 séances de prix
consécutives se terminant à D (c'est exactement ce que teste
`has_full[i] = np.isfinite(window).all(axis=0)` sur le calendrier union).
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRICES_EXT = ROOT / "data" / "pead" / "prices_extended"
PRICES_ORIG = ROOT / "data" / "pead" / "prices"
LOOKBACK = 252

CENSUS_DATES = ["1990-01-01", "1995-01-01", "2000-01-01", "2003-01-01",
                "2005-01-01", "2006-01-01", "2007-01-01", "2008-01-01",
                "2010-01-01", "2013-01-01", "2015-01-01", "2018-01-01",
                "2020-01-01", "2022-01-03", "2026-01-01"]


def load_first_dates(prices_dir):
    first, n_obs = {}, {}
    for path in sorted(prices_dir.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) == 0:
            continue
        first[path.stem] = close.index[0]
        n_obs[path.stem] = close
    return first, n_obs


def main():
    first_ext, series_ext = load_first_dates(PRICES_EXT)
    first_orig, _ = load_first_dates(PRICES_ORIG)
    total_ext = len(series_ext)

    lines = ["# Recensement de l'univers NDX-100 par date (cycle #163, AVANT pré-enregistrement)",
             "",
             "**Aucune performance de stratégie n'est calculée dans ce document** — uniquement la "
             "disponibilité des prix. Produit par `scripts/nonml_ndx100_universe_census.py`, "
             "committé AVANT `PREREG_leaders_index52w_high_overlay_defensible_window.md` pour "
             "justifier chiffrément le choix de la borne de début (Règle 1 + Règle 6).",
             "",
             f"Source : `data/pead/prices_extended/` ({total_ext} titres exploitables, liste de "
             f"constituants NDX-100 **de 2026**). Comparaison : `data/pead/prices/` "
             f"({len(first_orig)} titres, borne artificielle 2021 du protocole PEAD).",
             "",
             "## Titres éligibles par date",
             "",
             "Éligible à la date D = dispose de 252 séances de prix se terminant à D (critère "
             "identique à `has_full` dans `build_weights()`, aucun changement de logique).",
             "",
             "| Date | Titres éligibles | % du plateau (103) | Titres manquants |",
             "|---|---|---|---|"]

    elig_by_date = {}
    for d in CENSUS_DATES:
        D = pd.Timestamp(d)
        elig = []
        for t, s in series_ext.items():
            hist = s[s.index <= D]
            if len(hist) >= LOOKBACK:
                elig.append(t)
        elig_by_date[d] = sorted(elig)
        lines.append(f"| {d} | {len(elig)} | {100*len(elig)/total_ext:.0f}% | "
                     f"{total_ext - len(elig)} |")

    lines += ["",
              "## Titres absents (pas encore 252 séances) aux bornes candidates",
              ""]
    for d in ("2000-01-01", "2005-01-01", "2008-01-01", "2010-01-01"):
        missing = sorted(set(series_ext) - set(elig_by_date[d]))
        lines.append(f"**{d}** — {len(missing)} manquants : " +
                     (", ".join(missing) if missing else "aucun"))
        lines.append("")

    lines += ["## Première date de cotation disponible, par titre", "",
              "| Ticker | 1re séance (étendu) | 1re séance (`prices/`) |",
              "|---|---|---|"]
    for t in sorted(first_ext):
        o = first_orig.get(t)
        lines.append(f"| {t} | {first_ext[t].date()} | "
                     f"{o.date() if o is not None else '--'} |")

    out = ROOT / "results" / "nonml_ndx100_universe_census.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:40]))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    sys.exit(main())
