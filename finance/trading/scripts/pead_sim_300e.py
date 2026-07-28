"""Simulation — 300 EUR investis dans le portefeuille PEAD long-short
(dollar-neutre), sur toute la période du backtest pré-enregistré.

Consomme `finance/trading/data/pead/pead_portfolio_returns.csv` (série
journalière déjà nette de coûts, produite par pead_backtest.py -- aucun
recalcul, aucun paramètre retouché ici). Illustratif, pas un nouveau test
d'hypothèse : le verdict PASS/FAIL reste celui de
`results/pead_backtest_result.md`.

Note de mise à l'échelle : le rendement du CSV est un spread long-court
pour 1 unité de capital engagée de chaque côté (convention académique
"portefeuille long-moins-court"). Pour un compte de 300 EUR, on simule
100% du capital exposé au spread (pas de levier ajouté ici, à la
différence des simulations BH -- le spread lui-même est déjà une position
dollar-neutre, donc "sans levier" signifie 1x le spread, pas 1x un seul
côté).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "pead" / "pead_portfolio_returns.csv"
CAPITAL0 = 300.0


def main():
    if not CSV_PATH.exists():
        print(f"ERREUR : {CSV_PATH} introuvable — lancer pead_backtest.py d'abord.")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH, index_col=0, parse_dates=True)
    r = df["port_ret"].values
    dates = df.index

    equity = CAPITAL0 * np.cumprod(1.0 + r)
    running_max = np.maximum.accumulate(equity)
    dd = equity / running_max - 1.0
    mdd = dd.min() * 100

    ann = np.sqrt(252)
    sharpe_ann = (r.mean() / r.std()) * ann if r.std() > 0 else float("nan")
    n_years = len(r) / 252.0
    cagr = (equity[-1] / CAPITAL0) ** (1.0 / n_years) - 1.0 if n_years > 0 else float("nan")

    lines = [
        "# Simulation — 300 EUR dans le portefeuille PEAD long-short",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(r)} jours actifs, "
        f"~{n_years:.1f} ans). Capital de départ : {CAPITAL0:.0f} EUR, exposition 1x "
        "le spread long-court (dollar-neutre, pas de levier ajouté).",
        "",
        f"- **Capital final : {equity[-1]:.2f} EUR** ({100*(equity[-1]/CAPITAL0-1):+.1f}% sur la période)",
        f"- CAGR équivalent : {100*cagr:+.1f}%/an",
        f"- MDD (spread) : {mdd:.1f}%",
        f"- Sharpe annualisé : {sharpe_ann:+.2f}",
        "",
        "## Courbe de capital (échantillonnée)",
        "",
        "| Date | Capital (EUR) |",
        "|---|---|",
    ]
    step = max(1, len(equity) // 25)
    for i in range(0, len(equity), step):
        lines.append(f"| {dates[i].date()} | {equity[i]:.2f} |")
    lines.append(f"| {dates[-1].date()} | {equity[-1]:.2f} |")

    lines.append("")
    lines.append(
        "**Lecture honnête** : ce chiffre n'a de sens QUE si le critère pré-enregistré "
        "de `results/pead_backtest_result.md` est atteint (PASS) — sinon cette courbe "
        "décrit un backtest qui a officiellement échoué son propre test de robustesse "
        "(dégradation design→test excessive et/ou t-stat<2), et 300 EUR dedans serait "
        "irrationnel malgré une éventuelle jolie courbe apparente. Vérifier le verdict "
        "AVANT de lire ce chiffre comme une promesse."
    )

    out = ROOT / "results" / "pead_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
