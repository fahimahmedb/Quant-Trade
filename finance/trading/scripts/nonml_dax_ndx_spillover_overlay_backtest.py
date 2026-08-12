"""Backtest — Spillover cross-marché DAX->NDX (spécification
pré-enregistrée dans PREREG_dax_ndx_spillover_overlay.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Règle de succès
renforcée.
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
CAP = 2.0


def load_close_series(fname: str) -> pd.Series:
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    quality_report(df)
    return pd.Series(df["close"].values, index=pd.to_datetime(df["date"]))


def spillover_gate(ndx_dates: pd.DatetimeIndex, dax_close: pd.Series) -> np.ndarray:
    """Renvoie un masque booleen aligne sur ndx_dates : True au jour t
    si dax_ret(t-1) > 0, ou dax_ret(t-1) = rendement DAX de la seance
    de bourse PRECEDENTE (decalage explicite d'une seance, sans
    ambiguite de fuseau horaire -- correction du bug initial qui
    utilisait dax_ret(t), chevauchant partiellement la seance NDX du
    meme jour). Intersection stricte des dates NDX/DAX, pas de ffill."""
    dax_ret = dax_close.pct_change()
    dax_ret_lagged = dax_ret.shift(1)  # rendement de la seance DAX precedente
    common = dax_ret_lagged.reindex(ndx_dates)  # NaN si pas de date DAX exacte
    return (common > 0).fillna(False).values


def main():
    ndx_df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(ndx_df)
    ndx_close_vals = ndx_df["close"].values
    ndx_dates = pd.to_datetime(ndx_df["date"])

    dax_close = load_close_series("dax_daily.txt")

    gate_full = spillover_gate(ndx_dates, dax_close)  # aligne sur ndx_dates (longueur T)

    bh_full = np.log(ndx_close_vals[1:] / ndx_close_vals[:-1])
    # gate_full[t] = DAX(t-1)>0, connu bien avant l'ouverture NDX du
    # jour t -> applique au rendement NDX du jour t (bh_full[i] =
    # rendement de close(i) a close(i+1), attribue au jour i+1), donc
    # gate pour bh_full[i] = gate_full[i+1]
    mask = gate_full[1:]

    pos = np.where(mask, CAP, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok

    n_common = int(gate_full.sum())
    lines = [
        "# Résultat — Spillover cross-marché DAX->NDX (pré-enregistré, règle renforcée)",
        "",
        f"Position 1.0x en permanence, CAP={CAP}x les jours où le rendement DAX de la séance "
        f"de bourse PRÉCÉDENTE est strictement positif. "
        f"{len(bh_full)} séances testables, porte active {100*mask.mean():.1f}% du temps "
        f"({n_common} jours DAX(t-1) positifs sur dates communes).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay spillover DAX→NDX** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_dax_ndx_spillover_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
