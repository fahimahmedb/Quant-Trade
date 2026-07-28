"""Robustesse — Effet tournant de mois.

La fenêtre 4j/3j (Lakonishok & Smidt 1988) n'est PAS retunée ici -- on
vérifie seulement qu'un léger changement de largeur de fenêtre (±1 jour,
soit environ ±20-25% de la fenêtre de 7 jours) donne un résultat dans le
même ordre de grandeur (plateau), pas un effondrement soudain qui
trahirait un pic isolé/overfit sur la définition exacte 4/3. Aucun de ces
résultats alternatifs n'est utilisé pour retunér le critère PASS déjà
acquis avec 4j/3j -- purement diagnostique.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}
GRID = [(3, 2), (4, 3), (5, 4)]  # (last_n, first_n) -- 4/3 = specification pre-enregistree (centre)


def tom_mask(dates: pd.Series, last_n: int, first_n: int) -> np.ndarray:
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    df["rank_asc"] = df.groupby("ym").cumcount() + 1
    df["rank_desc"] = df.groupby("ym")["date"].transform(lambda s: len(s)) - df["rank_asc"] + 1
    mask = (df["rank_asc"] <= first_n) | (df["rank_desc"] <= last_n)
    return mask.values


def main():
    lines = [
        "# Robustesse — Effet tournant de mois (grille de plausibilité, PAS un retuning)",
        "",
        "Fenêtre pré-enregistrée (4j/3j) au centre de la grille ; ±1 jour testé pour "
        "vérifier un plateau. Le verdict PASS officiel reste celui de 4j/3j "
        "(`results/nonml_turn_of_month_result.md`) — ceci est diagnostique uniquement.",
        "",
        "| Fenêtre (derniers/premiers) | Nb marchés où ToM bat BH (/5) |",
        "|---|---|",
    ]
    for last_n, first_n in GRID:
        n_success = 0
        for name, fname in MARKETS.items():
            path = REPO_ROOT / "data" / fname
            if not path.exists():
                continue
            df = load_ohlc(str(path))
            quality_report(df)
            close = df["close"].values
            bh_full = np.log(close[1:] / close[:-1])
            mask = tom_mask(df["date"], last_n, first_n)[1:]
            pos = mask.astype(float)
            turn = np.abs(np.diff(pos, prepend=0.0))
            pnl_tom = pos * bh_full - turn * (COST_BPS / 1e4)
            pnl_bh = bh_full.copy()
            pnl_bh[0] -= COST_BPS / 1e4
            me_tom = trading_metrics(pnl_tom)
            me_bh = trading_metrics(pnl_bh)
            n_success += int(me_tom["sharpe_ann"] > me_bh["sharpe_ann"])
        marker = " ← spécification pré-enregistrée" if (last_n, first_n) == (4, 3) else ""
        lines.append(f"| {last_n}j / {first_n}j | {n_success}/5{marker} |")

    lines.append("")
    lines.append(
        "**Lecture** : si les résultats voisins (3j/2j et 5j/4j) restent proches de 4/5 "
        "ou 5/5, l'effet est un plateau plausible, pas un pic isolé sur la définition "
        "académique exacte. Un effondrement à 0-1/5 sur les fenêtres voisines "
        "indiquerait au contraire une définition très fragile."
    )

    out = ROOT / "results" / "nonml_turn_of_month_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
