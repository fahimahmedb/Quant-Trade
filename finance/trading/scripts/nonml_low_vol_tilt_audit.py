"""Audit adversarial — Low-Volatility Tilt.

1. Vérifie que le portefeuille low-vol a bien une volatilité RÉALISÉE
   inférieure au Buy&Hold (sanity check direct de la construction).
2. Test anti-lookahead (mutation des données récentes).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_low_vol_tilt_backtest import build_universe, VOL_WINDOW, REBAL_EVERY, TERCILE  # noqa: E402


def main():
    P = build_universe()
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0
    vol = P.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values

    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowvol = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    start = VOL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        v = vol[t]
        elig = np.where(np.isfinite(v) & exists[t])[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(v[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowvol[t:end] = w
        listed = exists[t]
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    pnl_lv = (weights_lowvol[start:] * R[start:]).sum(axis=1)
    pnl_b = (weights_bh[start:] * R[start:]).sum(axis=1)
    ann = np.sqrt(252)
    vol_lv_realized = pnl_lv.std() * ann
    vol_bh_realized = pnl_b.std() * ann

    lines = ["# Audit adversarial — Low-Volatility Tilt", "",
             "## 1. Sanity check : le portefeuille low-vol a-t-il vraiment une volatilité réalisée plus faible ?",
             "",
             f"Vol réalisée annualisée low-vol : {100*vol_lv_realized:.1f}%",
             f"Vol réalisée annualisée Buy&Hold : {100*vol_bh_realized:.1f}%",
             f"**{'OK — le portefeuille low-vol a bien une volatilité réalisée inférieure, construction cohérente avec son nom.' if vol_lv_realized < vol_bh_realized else 'SUSPECT — le portefeuille low-vol n’a PAS une volatilité inférieure au Buy&Hold, incohérence à investiguer.'}**",
             ""]

    # --- anti-lookahead ---
    cut = int(T * 0.8)
    rng = np.random.default_rng(5)
    P_mut = P.copy()
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    vol_mut = P_mut.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values
    check_i = cut - 30
    diff = np.abs(np.nan_to_num(vol[check_i], nan=0.0) - np.nan_to_num(vol_mut[check_i], nan=0.0)).max()
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    lines.append(f"Écart sur la vol réalisée à un jour antérieur à la mutation : {diff:.2e}")
    lines.append(f"**{'OK — aucune fuite.' if diff < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_low_vol_tilt_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
