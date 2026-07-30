"""Backtest — Pente de la courbe des taux US (T10Y2Y) appliquée au S&P
500 (mécanisme IDENTIQUE au #114, seul le marché piloté change,
spécification pré-enregistrée dans
PREREG_yield_curve_slope_sp500_vol_targeting_overlay.md, committée
avant ce script). n_trials=1 pour ce marché précis. Règle de succès
renforcée niveau 1 -- SI PASS, ce résultat n'est PAS final, voir Règle
9 (`scripts/nonml_pass_validation_battery.py`).
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
from nonml_yield_curve_slope_vol_targeting_overlay_backtest import (  # noqa: E402
    load_t10y2y, MEDIAN_WINDOW, combined_position, CAP, COST_BPS,
)

MARKET_FILE = "sp500_daily.txt"


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    slope = load_t10y2y()
    slope_lagged = slope.shift(1)
    median_slope = slope_lagged.rolling(MEDIAN_WINDOW).median()
    gate_series = (slope_lagged >= median_slope)
    gate_series_filled = gate_series.fillna(False)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = combined_position(bh_full, gate_aligned)

    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, 20)

    bh_t = bh_full[start:]
    pos = pos_full[start:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok

    gate_active = (pos > 1.0)
    lines = [
        "# Résultat — Pente de la courbe des taux US (T10Y2Y) appliquée au S&P 500 (pré-enregistré, règle renforcée niveau 1)",
        "",
        f"Mécanisme identique au #114 (NDX), seul le marché piloté change (S&P 500). "
        f"{len(bh_t)} séances testables.",
        "",
        f"%j porte pente courbe active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (S&P 500) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté pente courbe des taux** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS (niveau 1)' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py yield_curve_slope_sp500_vol_targeting_overlay` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_yield_curve_slope_sp500_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        dates_used = dates_idx.values[1:][start:]
        np.savez(
            ROOT / "results" / "nonml_yield_curve_slope_sp500_vol_targeting_overlay_pnl.npz",
            pos=pos, r_asset=bh_t, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
