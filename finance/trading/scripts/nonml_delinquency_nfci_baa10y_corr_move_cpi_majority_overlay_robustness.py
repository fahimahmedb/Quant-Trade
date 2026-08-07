"""Robustesse — cycle #365 (panel élargi 6 signaux +CPI, vote ≥5/6),
perturbation ±20% du plancher CUT=0.5x, seul paramètre non central au
critère de succès (le critère porte sur la règle de vote ≥5/6, pas sur
la valeur exacte du plancher). Ce n'est PAS un retuning : le verdict
reste celui du point pré-enregistré 0.5x. Grille réutilisée telle
quelle du #200/#284/#289/#296/#299/#304/#363 (Règle 7).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_delinquency_nfci_combined_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, expanding_tercile_gate_high,
)
from nonml_credit_card_delinquency_overlay_backtest import (  # noqa: E402
    build_delinquency_series, load_delinquency_lag,
)
from nonml_financial_conditions_overlay_backtest import (  # noqa: E402
    build_nfci_series, load_nfci_lag,
)
from nonml_credit_spread_overlay_backtest import load_baa10y_lag  # noqa: E402
from nonml_cross_market_correlation_ndx_dax_overlay_backtest import (  # noqa: E402
    build_corr_series, load_corr_lag,
)
from nonml_bond_market_volatility_overlay_backtest import (  # noqa: E402
    load_move_lag, load_move_series,
)
from nonml_cpi_inflation_overlay_backtest import (  # noqa: E402
    build_cpi_growth_series, load_cpi_growth_lag,
)

CUT_GRID = [round(CUT * 0.8, 2), CUT, round(CUT * 1.2, 2)]


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.cumprod(1.0 + pnl)[-1] - 1.0)
    return me, ret


def main():
    delinq_series = build_delinquency_series()
    nfci_series = build_nfci_series()
    corr_series = build_corr_series()
    move_series = load_move_series()
    cpi_series = build_cpi_growth_series()

    lines = [
        "# Robustesse — cycle #365, perturbation ±20% du plancher CUT",
        "",
        f"Point pré-enregistré : CUT = {CUT}x. Grille : {{{', '.join(f'{c}x' for c in CUT_GRID)}}}. "
        "La règle de vote elle-même (≥5/6 signaux dans leur tercile expanding le plus haut) n'est "
        "pas perturbée — seul le plancher de position l'est.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (0.5x) quelle que soit la lecture de ce tableau.",
        "",
        "| Marché | CUT | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |",
        "|---|---|---|---|---|---|---|---|",
    ]
    n_both_total, n_cells_total = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        delinq_lag = load_delinquency_lag(dates, delinq_series)[1:]
        nfci_lag = load_nfci_lag(dates, nfci_series)[1:]
        baa10y_lag = load_baa10y_lag(dates)[1:]
        corr_lag = load_corr_lag(dates, corr_series)[1:]
        move_lag = load_move_lag(dates, move_series)[1:]
        cpi_lag = load_cpi_growth_lag(dates, cpi_series)[1:]
        valid = (np.isfinite(delinq_lag) & np.isfinite(nfci_lag)
                 & np.isfinite(baa10y_lag) & np.isfinite(corr_lag)
                 & np.isfinite(move_lag) & np.isfinite(cpi_lag))
        start = int(np.argmax(valid))

        votes = (expanding_tercile_gate_high(delinq_lag).astype(int)
                 + expanding_tercile_gate_high(nfci_lag).astype(int)
                 + expanding_tercile_gate_high(baa10y_lag).astype(int)
                 + expanding_tercile_gate_high(corr_lag).astype(int)
                 + expanding_tercile_gate_high(move_lag).astype(int)
                 + expanding_tercile_gate_high(cpi_lag).astype(int))
        gate_majority = votes >= 5
        gate_t = gate_majority[start:]
        bh_t = bh_full[start:]

        for cut in CUT_GRID:
            pos = np.where(gate_t, cut, 1.0)
            me, ret = evaluate(pos, bh_t, COST_BPS)
            me_bh_local, ret_bh_local = evaluate(np.ones_like(bh_t), bh_t, COST_BPS)

            sharpe_ok = me["sharpe_ann"] > me_bh_local["sharpe_ann"]
            ret_ok = ret > ret_bh_local
            both_ok = sharpe_ok and ret_ok
            n_cells_total += 1
            n_both_total += int(both_ok)

            marker = " (point pré-enregistré)" if cut == CUT else ""
            lines.append(
                f"| {name}{marker} | {cut}x | {me['sharpe_ann']:+.2f} | "
                f"{100*ret:+.1f}% | {me['max_drawdown_pct']:.1f}% | "
                f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                f"{'OUI' if both_ok else 'non'} |"
            )

    lines.append("")
    lines.append(f"**{n_both_total}/{n_cells_total} cellules de la grille battent Buy&Hold "
                 f"sur les deux jambes (Sharpe ET rendement).**")

    out = ROOT / "results" / "nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
