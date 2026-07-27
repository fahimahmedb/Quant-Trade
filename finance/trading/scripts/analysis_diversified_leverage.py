"""Analyse — Diversification (4 marchés) + levier à risque égalisé.

Contexte : plutôt que prédire ou piloter le risque d'un seul actif, on
teste si COMBINER plusieurs marchés actions peu corrélés réduit le risque
du portefeuille sans réduire son rendement proportionnellement — ce qui
permettrait ensuite d'appliquer un levier plus fort pour un même budget de
risque qu'un seul indice concentré (logique "risk parity").

LIMITE DE DONNÉES ASSUMÉE ET SIGNALÉE : seuls des indices ACTIONS sont
disponibles ici (NDX, Russell 2000, S&P 500, DAX) — pas d'obligations, d'or
ni de matières premières. Les marchés actions sont structurellement
corrélés entre eux (davantage encore en période de stress) : la
diversification testée ici est donc partielle par construction, pas une
vraie diversification multi-classes d'actifs. Signalé explicitement dans
le rapport, pas présenté comme plus robuste que ce qu'il est.

Fenêtre commune : 01/11/1999 (début DAX, l'historique le plus court) au
10/07/2026, seule fenêtre où les 4 marchés ont des données.

Méthode (fixée a priori, pas ajustée après résultat) :
- Poids = inverse de la volatilité réalisée glissante 60j (risk parity
  simple, causal — n'utilise que les rendements passés), renormalisés à
  somme 1, rebalancement tous les 21j (même cadence que le reste du
  projet).
- Portefeuille diversifié non-levé vs chaque indice seul (Buy & Hold) sur
  la MÊME fenêtre commune.
- Portefeuille diversifié LEVÉ pour égaliser sa volatilité réalisée à
  celle du meilleur indice seul (Sharpe le plus élevé), comparaison du
  rendement à risque égal (pas de levier illimité : plafond CAP=3.0 fixé
  a priori, même logique que l'analyse Kelly).
"""
import os
import sys
import warnings
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from prediction import backtest, trading_metrics  # noqa: E402

COST_BPS = 5.0
VOL_WINDOW = 60
REBAL_EVERY = 21
CAP = 3.0
ANNUALIZE = np.sqrt(252)

MARKETS = {
    "NDX": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    series = {}
    for name, fname in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        r = log_returns_pct(df) / 100.0
        series[name] = r

    # Intersection des dates communes aux 4 marchés (aucune fuite : simple alignement calendaire)
    common_idx = series["NDX"].index
    for name in MARKETS:
        common_idx = common_idx.intersection(series[name].index)
    common_idx = common_idx.sort_values()
    R = pd.DataFrame({name: series[name].reindex(common_idx) for name in MARKETS}).dropna()
    T = len(R)
    names = list(MARKETS.keys())
    corr = R.corr()

    lines = [
        "# Analyse — Diversification (4 marchés actions) + levier à risque égalisé",
        "",
        f"Fenêtre commune : {R.index[0].date()} → {R.index[-1].date()} ({T} obs, "
        f"~{T/252:.1f} ans). **Limite assumée : 4 indices ACTIONS uniquement — pas "
        "de vraie diversification multi-classes d'actifs (pas d'obligations/or/"
        "matières premières disponibles).**",
        "",
        "## Corrélations des rendements quotidiens (fenêtre commune)",
        "",
        "| | " + " | ".join(names) + " |",
        "|---|" + "---|" * len(names),
    ]
    for n1 in names:
        lines.append(f"| {n1} | " + " | ".join(f"{corr.loc[n1, n2]:.2f}" for n2 in names) + " |")
    lines.append("")

    # --- portefeuille risk-parity simple (poids = 1/vol realisee glissante, causal) ---
    vol_roll = R.rolling(VOL_WINDOW).std()
    T0 = VOL_WINDOW + 5
    weights = pd.DataFrame(index=R.index, columns=names, dtype=float)
    for t in range(T0, T, REBAL_EVERY):
        block = range(t, min(t + REBAL_EVERY, T))
        inv_vol = 1.0 / vol_roll.iloc[t - 1].clip(lower=1e-8)
        w = inv_vol / inv_vol.sum()
        for tt in block:
            weights.iloc[tt] = w.values

    port_ret = (R * weights).sum(axis=1)
    idx = np.arange(T0, T)
    r_bt_port = port_ret.values
    pnl_port = backtest(np.ones(T), r_bt_port, COST_BPS)[idx]
    metr_port = trading_metrics(pnl_port)

    lines.append("## Portefeuille diversifié (risk parity, non levé) vs chaque marché seul")
    lines.append("")
    lines.append("| | Sharpe ann. | Vol ann. % | Calmar | MDD % | Rdt ann. % |")
    lines.append("|---|---|---|---|---|---|")
    lines.append(
        f"| **Portefeuille diversifié** | {metr_port['sharpe_ann']:+.2f} | "
        f"{100*ANNUALIZE*port_ret.values[idx].std():.1f} | {metr_port['calmar']:+.2f} | "
        f"{metr_port['max_drawdown_pct']:.1f} | {metr_port['ann_return_pct']:+.1f} |"
    )
    single_metrics = {}
    for name in names:
        pnl = backtest(np.ones(T), R[name].values, COST_BPS)[idx]
        me = trading_metrics(pnl)
        single_metrics[name] = me
        lines.append(
            f"| {name} (seul) | {me['sharpe_ann']:+.2f} | "
            f"{100*ANNUALIZE*R[name].values[idx].std():.1f} | {me['calmar']:+.2f} | "
            f"{me['max_drawdown_pct']:.1f} | {me['ann_return_pct']:+.1f} |"
        )
    lines.append("")

    best_single = max(single_metrics, key=lambda n: single_metrics[n]["sharpe_ann"])
    best_vol_ann = 100 * ANNUALIZE * R[best_single].values[idx].std()
    port_vol_ann = 100 * ANNUALIZE * port_ret.values[idx].std()
    lever = min(CAP, best_vol_ann / port_vol_ann) if port_vol_ann > 0 else 1.0

    pnl_levered = backtest(np.full(T, lever), r_bt_port, COST_BPS)[idx]
    metr_levered = trading_metrics(pnl_levered)

    lines.append(f"## Portefeuille diversifié LEVÉ à risque égalisé sur {best_single} (meilleur Sharpe seul)")
    lines.append("")
    lines.append(f"Levier appliqué = min(CAP={CAP:.1f}, vol({best_single})/vol(diversifié)) = **{lever:.2f}×**")
    lines.append("")
    lines.append("| | Sharpe ann. | Vol ann. % | Calmar | MDD % | Rdt ann. % |")
    lines.append("|---|---|---|---|---|---|")
    lines.append(
        f"| {best_single} (seul, référence) | {single_metrics[best_single]['sharpe_ann']:+.2f} | "
        f"{best_vol_ann:.1f} | {single_metrics[best_single]['calmar']:+.2f} | "
        f"{single_metrics[best_single]['max_drawdown_pct']:.1f} | "
        f"{single_metrics[best_single]['ann_return_pct']:+.1f} |"
    )
    lines.append(
        f"| **Diversifié × {lever:.2f}** | {metr_levered['sharpe_ann']:+.2f} | "
        f"{100*ANNUALIZE*(lever*port_ret.values[idx]).std():.1f} | {metr_levered['calmar']:+.2f} | "
        f"{metr_levered['max_drawdown_pct']:.1f} | {metr_levered['ann_return_pct']:+.1f} |"
    )
    lines.append("")

    gain = metr_levered["ann_return_pct"] - single_metrics[best_single]["ann_return_pct"]
    verdict_verbe = "apporte" if gain > 0 else "n'apporte pas"
    verdict_raison = (
        "bénéfice de diversification réel"
        if gain > 0
        else "pas de bénéfice net, la corrélation entre indices actions est trop élevée pour ce panier"
    )
    lines.append(
        f"**Verdict honnête** : à volatilité annualisée égalisée (~{best_vol_ann:.1f}%), "
        f"le portefeuille diversifié levé {verdict_verbe} "
        f"un supplément de rendement de {gain:+.1f} points annualisés vs {best_single} seul "
        f"({verdict_raison}). "
        "Rappel : ceci reste une diversification actions-actions uniquement — un vrai "
        "portefeuille risk-parity inclurait obligations/or/matières premières, non "
        "disponibles ici."
    )

    out = ROOT / "results" / "analysis_diversified_leverage.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
