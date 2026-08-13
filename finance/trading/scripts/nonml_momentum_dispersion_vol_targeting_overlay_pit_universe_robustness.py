"""Robustesse — dispersion du momentum, univers POINT-IN-TIME.

Grilles **identiques** à celles du cycle d'origine
(`nonml_momentum_dispersion_vol_targeting_overlay_robustness.py`) : CAP de
l'overlay et fenêtre de volatilité. Reprises telles quelles, elles sont donc
fixées avant toute exécution.

**Ce n'est PAS un retuning** : `LOOKBACK` (252), `SKIP` (21),
`MEDIAN_WINDOW` (252) et le seuil médian définissent l'hypothèse et restent
figés. On vérifie seulement que le PASS obtenu sur univers point-in-time est un
plateau et non un pic isolé.

Usage : python3 scripts/nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_robustness.py
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
import nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]
OUT = ROOT / "results" / "nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_robustness.md"


def position_for(r, gate_aligned, cap, vol_window):
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(vol_window).std().values * bt.ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt = bt.TARGET_VOL_ANNUAL / vol_lagged
    vt = np.clip(vt, 1.0, cap)
    vt = np.nan_to_num(vt, nan=1.0)
    return np.where(gate_r, vt, 1.0)


def run_one(r, gate_aligned, start, cap, vol_window):
    pos_full = position_for(r, gate_aligned, cap, vol_window)
    r_t = r[start:]
    pos = pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (bt.COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= bt.COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0
    return ((me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh),
            me_ov["sharpe_ann"], ret_ov)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    dates_idx = pd.to_datetime(df["date"])
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])

    disp, _cov = bt.compute_momentum_dispersion_series_pit()
    median_b = disp.rolling(bt.MEDIAN_WINDOW).median()
    # meme masque explicite qu'au backtest (piege du #396)
    signal_defined = disp.notna() & median_b.notna()
    gate_series = (disp >= median_b).where(signal_defined)
    gate_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(
        dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    valid = gate_raw.notna().values
    first_valid = int(np.argmax(valid)) if valid.any() else len(valid)

    L = ["# Robustesse — dispersion du momentum, univers POINT-IN-TIME", ""]
    L.append("Grilles **identiques** à celles du cycle d'origine, donc fixées avant exécution.")
    L.append("**Pas un retuning** : `LOOKBACK` (252), `SKIP` (21),")
    L.append("`MEDIAN_WINDOW` (252) et `MIN_LISTED` (10) définissent l'hypothèse et restent figés.")
    L.append("")
    L.append(f"CAP pré-enregistré = {bt.CAP}×, fenêtre de vol pré-enregistrée = {bt.VOL_WINDOW} j.")
    L.append("")

    L.append(f"## Grille CAP (fenêtre fixée à {bt.VOL_WINDOW} j)")
    L.append("")
    L.append("| CAP | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |")
    L.append("|---|---|---|---|")
    n_cap = 0
    for cap in CAP_GRID:
        start = max(first_valid, bt.VOL_WINDOW)
        ok, sh, ret = run_one(r, gate_aligned, start, cap, bt.VOL_WINDOW)
        n_cap += int(ok)
        mark = " ← pré-enregistré" if cap == bt.CAP else ""
        L.append(f"| {cap}×{mark} | {'OUI' if ok else 'non'} | {sh:+.2f} | {100*ret:+.1f}% |")
    L.append("")

    L.append(f"## Grille fenêtre de vol (CAP fixé à {bt.CAP}×)")
    L.append("")
    L.append("| Fenêtre | PASS (Sharpe ET rendement > BH) | Sharpe | Rendement total |")
    L.append("|---|---|---|---|")
    n_win = 0
    for w in WINDOW_GRID:
        start = max(first_valid, w)
        ok, sh, ret = run_one(r, gate_aligned, start, bt.CAP, w)
        n_win += int(ok)
        mark = " ← pré-enregistré" if w == bt.VOL_WINDOW else ""
        L.append(f"| {w} j{mark} | {'OUI' if ok else 'non'} | {sh:+.2f} | {100*ret:+.1f}% |")
    L.append("")

    L.append(f"**{n_cap}/{len(CAP_GRID)} cellules PASS sur la grille CAP, "
             f"{n_win}/{len(WINDOW_GRID)} sur la grille de fenêtre.** Rapporté tel quel, "
             f"sans réajustement.")
    L.append("")
    L.append("Le cycle d'origine (univers biaisé par le survivant) sert de point de")
    L.append("comparaison ; son rapport de robustesse est dans")
    L.append("`results/nonml_momentum_dispersion_vol_targeting_overlay_robustness.md`.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
