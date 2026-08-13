"""Robustesse — breadth de drawdown profond, univers POINT-IN-TIME.

Grilles de perturbation **identiques** à celles du cycle d'origine
(`nonml_deep_drawdown_breadth_vol_targeting_overlay_robustness.py`) : CAP et
fenêtre de volatilité. **Ce n'est PAS un retuning** — le seuil de drawdown
(-20 %) et la fenêtre de médiane (252j), qui sont au cœur du critère, restent
figés. On vérifie seulement que le PASS obtenu sur univers point-in-time est un
plateau et non un pic isolé.

Aucun paramètre n'est ajusté après lecture des résultats : la grille est reprise
telle quelle du cycle d'origine, donc fixée avant toute exécution.

Usage : python3 scripts/nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_robustness.py
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
import nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]
OUT = ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_robustness.md"


def position(r, gate_aligned, cap, window):
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(window).std().values * bt.ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt = bt.TARGET_VOL_ANNUAL / vol_lagged
    vt = np.clip(vt, 1.0, cap)
    vt = np.nan_to_num(vt, nan=1.0)
    return np.nan_to_num(np.where(gate_r, vt, 1.0), nan=1.0)


def evaluate(r, gate_aligned, cap, window, first_valid):
    pos_full = position(r, gate_aligned, cap, window)
    start = max(first_valid, window)
    r_t, pos = r[start:], pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (bt.COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= bt.COST_BPS / 1e4
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
    ret_ov = np.exp(pnl_ov.sum()) - 1.0
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ok = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
    return ok, me_ov["sharpe_ann"], ret_ov, me_ov["max_drawdown_pct"]


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    r = np.log(close[1:] / close[:-1])

    breadth_dd, _, _ = bt.compute_deep_drawdown_breadth_series_pit()
    median_dd = breadth_dd.rolling(bt.MEDIAN_WINDOW).median()
    signal_defined = breadth_dd.notna() & median_dd.notna()
    gate_series = (breadth_dd >= median_dd).where(signal_defined)
    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    valid = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)

    L = ["# Robustesse — breadth de drawdown profond, univers POINT-IN-TIME", ""]
    L.append("Grilles **identiques** à celles du cycle d'origine, donc fixées avant")
    L.append("exécution. **Pas un retuning** : le seuil de drawdown (−20 %) et la fenêtre")
    L.append("de médiane (252j), au cœur du critère, restent figés.")
    L.append("")
    L.append(f"CAP pré-enregistré = {bt.CAP}x, fenêtre pré-enregistrée = {bt.VOL_WINDOW}j.")
    L.append("")

    L.append(f"## Grille CAP (fenêtre fixée à {bt.VOL_WINDOW}j)")
    L.append("")
    L.append("| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement | MDD |")
    L.append("|---|---|---|---|---|")
    n_cap = 0
    for cap in CAP_GRID:
        ok, sh, ret, mdd = evaluate(r, gate_aligned, cap, bt.VOL_WINDOW, first_valid)
        n_cap += int(ok)
        mark = " ← CAP pré-enregistré" if cap == bt.CAP else ""
        L.append(f"| {cap}x | {'OUI' if ok else 'non'}{mark} | {sh:+.2f} | {100*ret:+.1f}% | {mdd:.1f}% |")
    L.append("")
    L.append(f"**{n_cap}/{len(CAP_GRID)} cellules PASS sur la grille CAP.**")
    L.append("")

    L.append(f"## Grille fenêtre de volatilité (CAP fixé à {bt.CAP}x)")
    L.append("")
    L.append("| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement | MDD |")
    L.append("|---|---|---|---|---|")
    n_win = 0
    for w in WINDOW_GRID:
        ok, sh, ret, mdd = evaluate(r, gate_aligned, bt.CAP, w, first_valid)
        n_win += int(ok)
        mark = " ← fenêtre pré-enregistrée" if w == bt.VOL_WINDOW else ""
        L.append(f"| {w}j | {'OUI' if ok else 'non'}{mark} | {sh:+.2f} | {100*ret:+.1f}% | {mdd:.1f}% |")
    L.append("")
    L.append(f"**{n_win}/{len(WINDOW_GRID)} cellules PASS sur la grille fenêtre.**")
    L.append("")
    L.append(f"## Lecture")
    L.append("")
    total = n_cap + n_win
    L.append(f"**{total}/{len(CAP_GRID)+len(WINDOW_GRID)} cellules PASS au total.** "
             f"Rapporté tel quel, sans réajustement.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
