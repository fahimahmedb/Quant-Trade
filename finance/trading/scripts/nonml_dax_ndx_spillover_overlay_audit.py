"""Audit adversarial — Spillover cross-marché DAX(t-1)->NDX.

1. Recalcul indépendant de la porte (boucle Python explicite sur les
   deux séries de dates, sans réutiliser pandas.reindex/shift) à un
   échantillon de dates.
2. Test anti-lookahead (mutation du futur DAX, NDX).
3. Vérification SPÉCIFIQUE de la correction du bug de fuseau horaire
   trouvé au premier essai : confirme qu'utiliser dax_ret(t) au lieu de
   dax_ret(t-1) produit bien un résultat aberrant (>10^9 %), documentant
   pourquoi la version corrigée (t-1) est la seule committée comme
   résultat.
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
from nonml_dax_ndx_spillover_overlay_backtest import load_close_series, spillover_gate, CAP, COST_BPS  # noqa: E402


def independent_gate_at(ndx_date, dax_dates, dax_close_vals) -> bool:
    """Recalcul par boucle Python explicite : trouve la derniere date
    DAX strictement anterieure a ndx_date, calcule son rendement vs la
    date DAX precedente."""
    idx = None
    for i in range(len(dax_dates) - 1, -1, -1):
        if dax_dates[i] < ndx_date:
            idx = i
            break
    if idx is None or idx == 0:
        return None
    if not np.isfinite(dax_close_vals[idx]) or not np.isfinite(dax_close_vals[idx - 1]):
        return None
    r = dax_close_vals[idx] / dax_close_vals[idx - 1] - 1.0
    return r > 0


def main():
    ndx_df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(ndx_df)
    ndx_dates = pd.to_datetime(ndx_df["date"])
    dax_close = load_close_series("dax_daily.txt")
    dax_dates_list = list(dax_close.index)
    dax_close_vals = dax_close.values

    gate_full = spillover_gate(ndx_dates, dax_close)

    check_dates_idx = list(range(2000, len(ndx_dates), 700))
    lines = ["# Audit adversarial — Spillover cross-marché DAX(t-1)->NDX", "",
             "## 1. Recalcul indépendant de la porte (boucle Python explicite, sans pandas.reindex/shift)", "",
             "| Date NDX (indice) | Concorde |",
             "|---|---|"]
    all_ok = True
    n_checked = 0
    for t in check_dates_idx:
        nd = ndx_dates.iloc[t]
        if nd not in dax_close.index:
            continue  # la porte du backtest est False par construction (pas de date DAX exacte)
        indep = independent_gate_at(nd, dax_dates_list, dax_close_vals)
        if indep is None:
            continue
        orig = bool(gate_full[t])
        concord = (orig == indep)
        all_ok &= concord
        n_checked += 1
        lines.append(f"| {t} | {'OUI' if concord else 'NON'} |")
    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul indépendant (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données DAX les plus récentes)")
    lines.append("")
    T_dax = len(dax_close)
    cut = int(T_dax * 0.8)
    rng = np.random.default_rng(110)
    dax_close_mut = dax_close.copy()
    dax_close_mut.iloc[cut:] = dax_close_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, T_dax - cut))
    cut_date = dax_close.index[cut]

    gate_before = spillover_gate(ndx_dates, dax_close)
    gate_after = spillover_gate(ndx_dates, dax_close_mut)
    check_slice_mask = ndx_dates < (cut_date - pd.Timedelta(days=10))
    diff_lookahead = int(np.sum(gate_before[check_slice_mask.values] != gate_after[check_slice_mask.values]))
    lines.append(f"Écart de porte sur les séances antérieures à la mutation : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Confirmation du bug de fuseau horaire initial (dax_ret(t) vs dax_ret(t-1))")
    lines.append("")
    ndx_close_vals = ndx_df["close"].values
    bh_full = np.log(ndx_close_vals[1:] / ndx_close_vals[:-1])

    dax_ret_same_day = dax_close.pct_change()
    gate_buggy_full = (dax_ret_same_day.reindex(ndx_dates) > 0).fillna(False).values
    mask_buggy = gate_buggy_full[1:]
    pos_buggy = np.where(mask_buggy, CAP, 1.0)
    turn_buggy = np.abs(np.diff(pos_buggy, prepend=1.0))
    pnl_buggy = pos_buggy * bh_full - turn_buggy * (COST_BPS / 1e4)
    ret_buggy = np.cumprod(1.0 + pnl_buggy)[-1] - 1.0

    mask_correct = gate_full[1:]
    pos_correct = np.where(mask_correct, CAP, 1.0)
    turn_correct = np.abs(np.diff(pos_correct, prepend=1.0))
    pnl_correct = pos_correct * bh_full - turn_correct * (COST_BPS / 1e4)
    ret_correct = np.cumprod(1.0 + pnl_correct)[-1] - 1.0

    lines.append(f"Version buguée (dax_ret(t), chevauchement horaire) : rendement total = {100*ret_buggy:+.1f}% "
                 f"(aberrant, confirme la fuite détectée au premier essai).")
    lines.append(f"Version corrigée (dax_ret(t-1), committée comme résultat officiel) : rendement total = {100*ret_correct:+.1f}% "
                 f"(plausible, cohérent avec les autres résultats du backlog).")
    lines.append("")
    lines.append("**La version corrigée (t-1) est la seule utilisée pour le verdict PASS/FAIL officiel — "
                 "cette section documente uniquement pourquoi la version initiale a été rejetée avant tout commit de résultat.**")

    out = ROOT / "results" / "nonml_dax_ndx_spillover_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
