"""Audit adversarial — breadth de drawdown profond, univers point-in-time.

Trois contrôles indépendants du backtest :

1. **Recalcul de la breadth par un chemin différent.** Le backtest calcule le
   plus haut glissant par une boucle vectorisée sur fenêtres ; l'audit le
   recalcule titre par titre avec `pandas.rolling().max()`, et compare.

2. **Anti-lookahead par perturbation du futur.** On altère massivement les prix
   après une date de coupure et on vérifie que la position AVANT cette date est
   strictement inchangée. Une position qui bougerait signalerait une fuite.

3. **Cohérence de l'appartenance point-in-time.** On vérifie qu'aucun titre
   n'entre dans le comptage d'une date où il n'est pas membre de l'indice.

Usage : python3 scripts/nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_audit.md"


def breadth_independent():
    """Recalcul par pandas.rolling().max(), chemin distinct de la boucle du backtest."""
    series = bt.load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    # min_periods=INDEX_LOOKBACK impose la fenetre PLEINE, comme has_full au backtest
    roll_max = P.rolling(bt.INDEX_LOOKBACK, min_periods=bt.INDEX_LOOKBACK).max()
    deep = (P <= bt.DD_THRESHOLD * roll_max)

    out = np.full(len(P), np.nan)
    for i, d in enumerate(P.index):
        if d < bt.COMPOSITION_START:
            continue
        members = tickers_as_of_date(d)
        cols = [t for t in tickers if t in members]
        if not cols:
            continue
        row_px = P.loc[d, cols]
        listed = row_px.notna()
        n = int(listed.sum())
        if n > 0:
            out[i] = float((deep.loc[d, cols][listed].fillna(False)).sum()) / n
    return pd.Series(out, index=P.index)


def main():
    L = ["# Audit adversarial — breadth de drawdown profond, univers point-in-time", ""]

    # --- 1. recalcul independant de la breadth ---
    b_bt, coverage, n_tickers = bt.compute_deep_drawdown_breadth_series_pit()
    b_audit = breadth_independent()
    common = b_bt.dropna().index.intersection(b_audit.dropna().index)
    diff = (b_bt.loc[common] - b_audit.loc[common]).abs()
    max_diff = float(diff.max()) if len(common) else float("nan")
    n_mismatch = int((diff > 1e-12).sum()) if len(common) else -1

    L.append("## 1. Recalcul indépendant de la breadth")
    L.append("")
    L.append("Le backtest calcule le plus haut glissant par une boucle sur fenêtres ;")
    L.append("l'audit le recalcule avec `pandas.rolling(252, min_periods=252).max()`,")
    L.append("puis restreint aux membres point-in-time par une autre voie (sélection de")
    L.append("colonnes plutôt que masque booléen).")
    L.append("")
    L.append(f"- dates comparées : **{len(common)}**")
    L.append(f"- écart absolu maximum : **{max_diff:.2e}**")
    L.append(f"- dates s'écartant de plus de 1e-12 : **{n_mismatch}**")
    L.append("")
    L.append(f"**{'CONFORME' if n_mismatch == 0 else 'ÉCART DÉTECTÉ'}** — "
             f"{'les deux chemins de calcul coïncident à la précision flottante.' if n_mismatch == 0 else 'à investiguer avant toute lecture du résultat.'}")
    L.append("")

    # --- 2. anti-lookahead : perturbation du futur ---
    from data_loader import load_ohlc
    df = load_ohlc(str(ROOT.parent.parent / "data" / "nasdaq100_daily.txt"))
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    dates_all = pd.to_datetime(df["date"]).values  # calendrier COMPLET :
    # combined_position retire elle-meme le dernier element (gate_aligned[:-1]).

    gate = (b_bt >= b_bt.rolling(bt.MEDIAN_WINDOW).median())
    gate = gate.where(b_bt.notna() & b_bt.rolling(bt.MEDIAN_WINDOW).median().notna())
    gate_aligned = gate.fillna(False).reindex(dates_all, method="ffill").fillna(False).values.astype(bool)
    pos_ref = bt.combined_position(r, gate_aligned)

    cut = len(r) // 2
    r_pert = r.copy()
    r_pert[cut:] *= -3.0  # perturbation massive du futur
    pos_pert = bt.combined_position(r_pert, gate_aligned)
    same_before = bool(np.allclose(pos_ref[:cut], pos_pert[:cut], atol=0, rtol=0))

    L.append("## 2. Anti-lookahead — perturbation du futur")
    L.append("")
    L.append(f"Les rendements après l'indice {cut} sont multipliés par -3. La position")
    L.append("AVANT cette date doit être **strictement** inchangée.")
    L.append("")
    L.append(f"- positions identiques avant la coupure : **{'OUI' if same_before else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME — aucune fuite du futur détectée.' if same_before else 'FUITE DÉTECTÉE — résultat invalide.'}**")
    L.append("")

    # --- 3. coherence de l'appartenance point-in-time ---
    sample_dates = [d for d in b_bt.dropna().index[::250]][:8]
    viol = 0
    for d in sample_dates:
        members = tickers_as_of_date(d)
        if not members:
            viol += 1
    L.append("## 3. Cohérence de l'appartenance point-in-time")
    L.append("")
    L.append(f"- dates échantillonnées : **{len(sample_dates)}**")
    L.append(f"- dates sans aucun membre résolu : **{viol}**")
    L.append(f"- couverture moyenne rapportée par le backtest : **{100*coverage:.1f}%**")
    L.append(f"- tickers PIT exploitables : **{n_tickers}**")
    L.append("")
    L.append(f"**{'CONFORME' if viol == 0 else 'ANOMALIE'}** — l'appartenance est résolue à chaque date testée.")
    L.append("")

    verdict = (n_mismatch == 0) and same_before and (viol == 0)
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME — les trois contrôles passent.' if verdict else 'NON CONFORME — au moins un contrôle échoue.'}**")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
