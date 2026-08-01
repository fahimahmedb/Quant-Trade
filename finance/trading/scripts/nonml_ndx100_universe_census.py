"""Recensement de l'univers NDX-100 par date + QUANTIFICATION DU BIAIS DU
SURVIVANT des cycles #161/#162 (cycle #163).

**Ce script ne calcule AUCUNE performance de stratégie** — uniquement la
composition de l'indice et la disponibilité des prix. Il est exécuté et
committé AVANT le pré-enregistrement du cycle #163 parce que son unique
rôle est de MESURER le problème (Règle 6 : traçabilité) et de justifier
chiffrément le périmètre du cycle. Aucun rendement, aucun Sharpe, aucun
signal n'est calculé ici — il est donc impossible de « choisir la fenêtre
qui donne le meilleur résultat ».

Deux mesures :

1. **Biais du survivant des cycles #161 (2022-2026) et #162 (1970-2026)** :
   ces deux cycles ont utilisé la liste des membres du NDX-100 **de 2026**
   (`data/pead/ndx100_constituents.json`) appliquée rétroactivement. On
   mesure ici, année par année, quelle fraction des VRAIS membres de
   l'indice à cette date figure dans cette liste — la fraction manquante
   est, par construction, composée des titres sortis de l'indice depuis
   (donc en moyenne des sous-performants) : c'est exactement le biais.

2. **Disponibilité des prix** : combien de titres disposent d'assez
   d'historique (252 séances) à différentes dates, dans les deux dossiers
   de prix déjà committés.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ndx100_membership import (  # noqa: E402
    tickers_as_of, all_tickers_ever, FIRST_YEAR, LAST_YEAR, UPSTREAM_VERSION, UPSTREAM_URL,
)

PRICES_EXT = ROOT / "data" / "pead" / "prices_extended"
PRICES_ORIG = ROOT / "data" / "pead" / "prices"
CONSTITUENTS_2026 = ROOT / "data" / "pead" / "ndx100_constituents.json"
LOOKBACK = 252

CENSUS_DATES = ["1990-01-01", "1995-01-01", "2000-01-01", "2005-01-01",
                "2008-01-01", "2010-01-01", "2013-01-01", "2015-01-01",
                "2016-01-01", "2018-01-01", "2020-01-01", "2022-01-03",
                "2026-01-01"]


def load_series(prices_dir):
    out = {}
    for path in sorted(prices_dir.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close):
            out[path.stem] = close
    return out


def main():
    series_ext = load_series(PRICES_EXT)
    series_orig = load_series(PRICES_ORIG)
    list_2026 = set(json.loads(CONSTITUENTS_2026.read_text()))
    ever = all_tickers_ever()

    lines = [
        "# Recensement de l'univers NDX-100 et mesure du biais du survivant (cycle #163)",
        "",
        "**Aucune performance de stratégie n'est calculée dans ce document** — uniquement "
        "la composition de l'indice et la disponibilité des prix. Produit par "
        "`scripts/nonml_ndx100_universe_census.py`, committé AVANT "
        "`PREREG_leaders_index52w_high_overlay_pit_universe.md` (Règle 1 : le pré-enregistrement "
        "doit fixer un périmètre justifié, pas deviné ; Règle 6 : traçabilité).",
        "",
        f"Source de composition point-in-time : `nasdaq-100-ticker-history` v{UPSTREAM_VERSION} "
        f"({UPSTREAM_URL}, licence MIT), données YAML vendorées verbatim dans "
        f"`data/ndx100_history/` et rechargées par `scripts/ndx100_membership.py` (portage "
        f"minimal vérifié contre les doctests amont). Couverture amont : {FIRST_YEAR}-01-01 → "
        f"au moins 2026-06-22.",
        "",
        f"**{len(ever)} tickers différents** ont appartenu au NDX-100 entre {FIRST_YEAR} et "
        f"{LAST_YEAR}, contre **{len(list_2026)}** dans la liste figée de 2026 utilisée par les "
        f"cycles #161 et #162.",
        "",
        "## 1. Biais du survivant des cycles #161/#162, mesuré année par année",
        "",
        "Les cycles #161 (fenêtre 2022-2026) et #162 (fenêtre 1970-2026) ont utilisé la liste "
        "des membres de 2026 appliquée rétroactivement. Le tableau donne, à chaque 1er janvier, "
        "le nombre de VRAIS membres de l'indice, combien d'entre eux figurent dans cette liste "
        "de 2026, et la fraction manquante — composée exclusivement de titres sortis de l'indice "
        "depuis, donc en moyenne des sous-performants (biais orienté à la HAUSSE des rendements).",
        "",
        "| Date | Vrais membres | Présents dans la liste 2026 | Couverture | Manquants (sortis depuis) |",
        "|---|---|---|---|---|",
    ]
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        real = tickers_as_of(year, 1, 1)
        covered = real & list_2026
        lines.append(f"| {year}-01-01 | {len(real)} | {len(covered)} | "
                     f"{100*len(covered)/len(real):.0f}% | {len(real)-len(covered)} |")
    lines += ["",
              "Exemples de membres réels absents de la liste 2026 (donc jamais investissables "
              "dans les cycles #161/#162) :", ""]
    for year in (2015, 2020, 2023):
        missing = sorted(tickers_as_of(year, 1, 1) - list_2026)
        lines.append(f"- **{year}** ({len(missing)} manquants) : " + ", ".join(missing))
    lines += ["",
              "## 2. Disponibilité des prix déjà committés",
              "",
              "Éligible à la date D = 252 séances de prix disponibles se terminant à D (critère "
              "identique à `has_full` dans `build_weights()`, aucun changement de logique).",
              "",
              "| Date | `prices_extended/` (103 titres, liste 2026) | `prices/` (99 titres, borne PEAD 2021) |",
              "|---|---|---|"]
    for d in CENSUS_DATES:
        D = pd.Timestamp(d)
        n_ext = sum(1 for s in series_ext.values() if len(s[s.index <= D]) >= LOOKBACK)
        n_org = sum(1 for s in series_orig.values() if len(s[s.index <= D]) >= LOOKBACK)
        lines.append(f"| {d} | {n_ext} | {n_org} |")

    lines += ["",
              "## 3. Prix manquants pour une reconstruction point-in-time",
              "",
              f"Une reconstruction sans biais du survivant sur {FIRST_YEAR}-{LAST_YEAR} exige les "
              f"prix des {len(ever)} tickers ayant appartenu à l'indice, pas seulement des "
              f"{len(list_2026)} membres actuels.",
              ""]
    missing_prices = sorted(ever - set(series_ext))
    lines.append(f"Tickers sans prix dans `data/pead/prices_extended/` : **{len(missing_prices)}** "
                 f"sur {len(ever)}.")
    lines.append("")
    lines.append(", ".join(missing_prices) if missing_prices else "aucun")
    lines.append("")

    out = ROOT / "results" / "nonml_ndx100_universe_census.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    sys.exit(main())
