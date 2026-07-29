"""Robustesse — Décomposition du turn-of-month, Variante A (fin de mois
seule, PASS). Grille CAP uniquement (PAS un retuning de LAST_N_DAYS),
autour de la valeur pré-enregistrée (CAP=2.0x). La Variante B (FAIL)
n'est pas testée en robustesse, conformément au protocole (robustesse
uniquement en cas de PASS).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_tom_decomposition_overlay_backtest import end_of_month_mask, COST_BPS, MARKETS  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]


def run_one(close: np.ndarray, mask_full: np.ndarray, cap: float) -> bool:
    bh_full = np.log(close[1:] / close[:-1])
    pos = np.where(mask_full[1:], cap, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    data = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            data[name] = (df["close"].values, end_of_month_mask(df["date"]))

    lines = [
        "# Robustesse — Décomposition ToM, Variante A (fin de mois seule) — grille CAP",
        "",
        "CAP pré-enregistré = 2.0x. Fenêtre LAST_N_DAYS=4 non retouchée.",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(close, mask, cap) for close, mask in data.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(data)}{marker} |")

    out = ROOT / "results" / "nonml_tom_decomposition_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
