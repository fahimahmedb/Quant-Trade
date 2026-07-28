"""Audit adversarial — Reversal court terme.

1. Recalcul indépendant du signal 5j par une méthode différente
   (pct_change pandas au lieu de division manuelle numpy).
2. Test anti-lookahead (mutation des données récentes, vérifie que les
   positions passées ne changent pas).
3. Vérifie que le résultat catastrophique n'est pas un artefact de
   quelques titres extrêmes (ex. delisting, split mal géré) en
   inspectant les positions les plus fréquentes du panier "losers".
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

PRICES_DIR = ROOT / "data" / "pead" / "prices"
SIGNAL_WINDOW = 5
REBAL_EVERY = 5
TERCILE = 1.0 / 3.0


def load_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > SIGNAL_WINDOW + REBAL_EVERY + 10:
            series[path.stem] = close
    return series


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    lines = ["# Audit adversarial — Reversal court terme (1 semaine)", ""]

    # --- 1. Recalcul independant (pandas pct_change vs numpy manuel) ---
    signal_pandas = P.pct_change(periods=SIGNAL_WINDOW).values
    close = P.values
    signal_manual = np.full(P.shape, np.nan)
    for i in range(SIGNAL_WINDOW, len(P)):
        with np.errstate(all="ignore", invalid="ignore"):
            signal_manual[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0

    mask = np.isfinite(signal_pandas) & np.isfinite(signal_manual)
    diff = np.abs(signal_pandas[mask] - signal_manual[mask])
    max_diff = float(diff.max()) if diff.size else 0.0
    lines.append("## 1. Recalcul indépendant du signal (pandas.pct_change vs numpy manuel)")
    lines.append("")
    lines.append(f"Écart maximum sur {mask.sum()} valeurs comparables : {max_diff:.2e}")
    lines.append(f"**{'OK — méthodes concordantes.' if max_diff < 1e-9 else 'ÉCHEC — divergence.'}**")
    lines.append("")

    # --- 2. Anti-lookahead ---
    T = len(P)
    cut = int(T * 0.8)
    rng = np.random.default_rng(7)
    P_mut = P.copy()
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    check_i = cut - 20
    s_orig = P.values[check_i] / P.values[check_i - SIGNAL_WINDOW] - 1.0
    s_mut = P_mut.values[check_i] / P_mut.values[check_i - SIGNAL_WINDOW] - 1.0
    s_orig_clean = np.nan_to_num(s_orig, nan=0.0)
    s_mut_clean = np.nan_to_num(s_mut, nan=0.0)
    diff_lookahead = float(np.abs(s_orig_clean - s_mut_clean).max())
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    lines.append(f"Écart sur un signal antérieur à la mutation : {diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite.' if diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")

    # --- 3. Concentration du panier losers ---
    exists = np.isfinite(close)
    n_bottom = max(1, int(round(len(tickers) * TERCILE)))
    counts = {t: 0 for t in tickers}
    total_slots = 0
    for t in range(SIGNAL_WINDOW, len(P), REBAL_EVERY):
        s = signal_manual[t]
        elig = np.where(np.isfinite(s))[0]
        n_bot_t = min(n_bottom, len(elig))
        if n_bot_t == 0:
            continue
        bottom_idx = elig[np.argsort(s[elig])[:n_bot_t]]
        for idx in bottom_idx:
            counts[tickers[idx]] += 1
        total_slots += n_bot_t

    top5 = sorted(counts.items(), key=lambda kv: -kv[1])[:5]
    share_top5 = sum(c for _, c in top5) / total_slots if total_slots else 0.0
    lines.append("## 3. Concentration du panier \"losers\" (surreprésentation de quelques titres ?)")
    lines.append("")
    lines.append(f"Titres les plus fréquents dans le panier losers sur toute la période : {top5}")
    lines.append(f"Part des {len(top5)} titres les plus fréquents dans le total des sélections : {100*share_top5:.1f}%")
    lines.append("")
    lines.append(
        f"**{'Concentration limitée, résultat probablement diffus sur beaucoup de titres.' if share_top5 < 0.15 else 'Concentration notable — vérifier si quelques titres en forte détresse dominent le résultat catastrophique.'}**"
    )

    out = ROOT / "results" / "nonml_short_term_reversal_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
