"""Robustesse — Overlay défensif EWMA. Grille de λ (seul paramètre libre
du composant EWMA), symétrique autour de 0.94 (défaut RiskMetrics
pré-enregistré) -- PAS un retuning après avoir vu quel λ "marche le
mieux".
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
import nonml_ewma_defensive_overlay_and_triple_engine_backtest as m  # noqa: E402

LAM_GRID = [0.90, 0.92, 0.94, 0.96, 0.98]


def ewma_position_with_lam(r, lam):
    T = len(r)
    s2_path = np.full(T, np.nan)
    for tr in range(m.T0, T, m.REFIT_EVERY):
        block_end = min(tr + m.REFIT_EVERY, T)
        mu_tr = r[:tr].mean()
        eps = r - mu_tr
        s2 = np.empty(T + 1)
        s2[0] = float(np.var(r[:tr] - mu_tr))
        for t in range(T):
            s2[t + 1] = lam * s2[t] + (1 - lam) * eps[t] ** 2
        s2_path[tr:block_end] = s2[tr:block_end]
    vol_ann = np.sqrt(np.maximum(s2_path, 0.0) * m.ANNUALIZATION2)
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = m.TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 0.0, m.CAP)
    return np.nan_to_num(pos, nan=1.0)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])

    lines = [
        "# Robustesse — Overlay défensif EWMA (grille de λ, PAS un retuning)",
        "",
        "λ pré-enregistré = 0.94 (défaut RiskMetrics).",
        "",
        "| λ | Sharpe ann. | Rendement total | Calmar | PASS standard | PASS Calmar |",
        "|---|---|---|---|---|---|",
    ]
    for lam in LAM_GRID:
        pos_full = ewma_position_with_lam(r, lam)
        pos_t = pos_full[m.T0:]
        r_t = r[m.T0:]
        turn = np.abs(np.diff(pos_t, prepend=1.0))
        pnl_ov = pos_t * r_t - turn * (m.COST_BPS / 1e4)
        pnl_bh = r_t.copy()
        pnl_bh[0] -= m.COST_BPS / 1e4
        me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
        ret_ov = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)
        ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)
        calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else -np.inf
        calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else -np.inf
        ok_std = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
        ok_calmar = calmar_ov > calmar_bh
        marker = " ← pré-enregistré" if lam == 0.94 else ""
        lines.append(
            f"| {lam:.2f} | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {calmar_ov:.3f} | "
            f"{'OUI' if ok_std else 'non'} | {'OUI' if ok_calmar else 'non'}{marker} |"
        )

    out = ROOT / "results" / "nonml_ewma_defensive_overlay_and_triple_engine_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
