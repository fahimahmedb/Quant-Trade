"""Backtest — Momentum absolu dual (rotation) NDX / proxy obligataire
(spécification pré-enregistrée dans
PREREG_dual_momentum_ndx_bond_rotation.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée niveau 1 --
SI PASS, résultat PAS final, voir Règle 9
(`scripts/nonml_pass_validation_battery.py`).
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
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy  # noqa: E402

COST_BPS = 5.0
MOMENTUM_WINDOW = 252


def month_end_mask(dates: pd.DatetimeIndex) -> np.ndarray:
    ym = pd.DatetimeIndex(dates).to_period("M")
    return (ym.values[1:] != ym.values[:-1])  # True au DERNIER jour de chaque mois (change le mois suivant)


def dual_momentum_position(r_ndx: np.ndarray, r_bond: np.ndarray, dates: pd.DatetimeIndex,
                            window: int = MOMENTUM_WINDOW) -> np.ndarray:
    dates = pd.DatetimeIndex(dates)
    T = len(r_ndx)
    cum_ndx = pd.Series(r_ndx).rolling(window).sum().values
    cum_bond = pd.Series(r_bond).rolling(window).sum().values

    is_month_end = np.zeros(T, dtype=bool)
    is_month_end[:-1] = month_end_mask(dates)
    is_month_end[-1] = True

    pos_ndx = np.full(T, np.nan)  # 1.0 = 100% NDX, 0.0 = 100% obligataire
    current = 1.0  # position par defaut avant le premier signal valide (convention neutre)
    for t in range(T):
        if is_month_end[t] and t >= window and np.isfinite(cum_ndx[t]) and np.isfinite(cum_bond[t]):
            current = 1.0 if cum_ndx[t] > cum_bond[t] else 0.0
        pos_ndx[t] = current
    # decale d'un jour : la decision prise a la cloture de t s'applique a partir de t+1 (causal)
    pos_ndx_shifted = np.roll(pos_ndx, 1)
    pos_ndx_shifted[0] = 1.0
    return pos_ndx_shifted


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_full = pd.to_datetime(df["date"]).iloc[1:]
    r_ndx_full = np.log(close[1:] / close[:-1])

    dgs10 = load_dgs10()
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")

    valid = r_bond_aligned.notna().values
    start0 = int(np.argmax(valid)) if valid.any() else len(valid)

    r_ndx0 = r_ndx_full[start0:]
    r_bond0 = r_bond_aligned.values[start0:]
    dates0 = dates_full[start0:]

    pos_ndx_full = dual_momentum_position(r_ndx0, r_bond0, dates0, MOMENTUM_WINDOW)

    start = MOMENTUM_WINDOW
    pos_ndx = pos_ndx_full[start:]
    r_ndx = r_ndx0[start:]
    r_bond = r_bond0[start:]
    dates_used = dates0.values[start:]

    r_combined = pos_ndx * r_ndx + (1.0 - pos_ndx) * r_bond
    turn = np.abs(np.diff(pos_ndx, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_ndx.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict_standard = sharpe_ok and ret_ok

    calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)
    calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
    calmar_ok = calmar_ov > calmar_bh
    verdict = verdict_standard or calmar_ok

    n_rotations = int(np.sum(np.abs(np.diff(pos_ndx)) > 0.5))
    frac_ndx = float(pos_ndx.mean())

    lines = [
        "# Résultat — Momentum absolu dual (rotation) NDX / proxy obligataire (pré-enregistré, deux critères)",
        "",
        f"Rebalancement mensuel : 100% NDX si momentum {MOMENTUM_WINDOW}j > momentum obligataire, "
        f"100% obligataire (DGS10) sinon. {len(r_ndx)} séances (fenêtre commune NDX ∩ DGS10, "
        f"après warmup {MOMENTUM_WINDOW}j).",
        "",
        f"Nombre de rotations complètes : {n_rotations} — % du temps en NDX : {100*frac_ndx:.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **Momentum dual (rotation)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% | {calmar_ov:.3f} |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        f"3. Critère standard (1 ET 2) : {'PASS' if verdict_standard else 'FAIL'}",
        f"4. Critère Calmar (overlay > BH) : {'PASS' if calmar_ok else 'FAIL'}",
        "",
        f"**{'PASS (niveau 1, au moins un critère)' if verdict else 'FAIL'}**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py dual_momentum_ndx_bond_rotation` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_dual_momentum_ndx_bond_rotation_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_dual_momentum_ndx_bond_rotation_pnl.npz",
            pos=pos_ndx, r_asset=r_ndx, r_alt=r_bond, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
