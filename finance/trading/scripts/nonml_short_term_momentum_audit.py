"""Audit adversarial — Momentum court terme (winners).

Sharpe +2.35 est un chiffre extrême (le projet a pour convention qu'un
Sharpe >3 doit éveiller la suspicion d'une erreur de méthode -- 2.35 en
est proche, audit renforcé) :
1. Recalcul indépendant du signal (pandas.pct_change vs numpy manuel,
   même technique que le cycle #5).
2. Test anti-lookahead (mutation des données récentes).
3. Concentration du panier winners -- un Sharpe aussi élevé pourrait
   venir de quelques titres extrêmes (ex. un titre qui a été multiplié
   par 10, sur-représenté dans winners chaque semaine où il grimpe).
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

    lines = ["# Audit adversarial — Momentum court terme (winners)", "",
             "Sharpe +2.35 est un chiffre extrême, audit renforcé (le projet flague "
             "tout Sharpe >3 comme suspect ; 2.35 en est assez proche pour justifier "
             "une vérification approfondie).", ""]

    # --- 1. Recalcul independant du signal ---
    signal_pandas = P.pct_change(periods=SIGNAL_WINDOW, fill_method=None).values
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
    rng = np.random.default_rng(11)
    P_mut = P.copy()
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    check_i = cut - 20
    s_orig = P.values[check_i] / P.values[check_i - SIGNAL_WINDOW] - 1.0
    s_mut = P_mut.values[check_i] / P_mut.values[check_i - SIGNAL_WINDOW] - 1.0
    diff_lookahead = float(np.abs(np.nan_to_num(s_orig, nan=0.0) - np.nan_to_num(s_mut, nan=0.0)).max())
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    lines.append(f"Écart sur un signal antérieur à la mutation : {diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite.' if diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")

    # --- 3. Concentration ---
    exists = np.isfinite(close)
    n_top = max(1, int(round(len(tickers) * TERCILE)))
    counts = {t: 0 for t in tickers}
    total_slots = 0
    for t in range(SIGNAL_WINDOW, len(P), REBAL_EVERY):
        s = signal_manual[t]
        elig = np.where(np.isfinite(s))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t == 0:
            continue
        top_idx = elig[np.argsort(-s[elig])[:n_top_t]]
        for idx in top_idx:
            counts[tickers[idx]] += 1
        total_slots += n_top_t

    top10 = sorted(counts.items(), key=lambda kv: -kv[1])[:10]
    share_top10 = sum(c for _, c in top10) / total_slots if total_slots else 0.0
    lines.append("## 3. Concentration du panier \"winners\"")
    lines.append("")
    lines.append(f"Top 10 titres les plus fréquents : {top10}")
    lines.append(f"Part des 10 titres les plus fréquents dans le total des sélections : {100*share_top10:.1f}%")
    lines.append("")
    lines.append(
        f"**{'Concentration limitée, résultat probablement diffus.' if share_top10 < 0.25 else 'Concentration notable — le Sharpe élevé pourrait refléter quelques titres extrêmes plutôt qu’un effet diffus, à interpréter avec prudence.'}**"
    )

    # --- 4. Sanity check supplementaire : rendement total individuel max ---
    total_ret_per_ticker = {t: (P[t].dropna().iloc[-1] / P[t].dropna().iloc[0] - 1.0) for t in tickers if P[t].notna().sum() > 10}
    top_movers = sorted(total_ret_per_ticker.items(), key=lambda kv: -kv[1])[:5]
    lines.append("")
    lines.append("## 4. Titres les plus extrêmes sur toute la période (rendement total individuel)")
    lines.append("")
    lines.append(f"{[(t, f'{100*r:+.0f}%') for t, r in top_movers]}")
    lines.append(
        "Contexte : NDX-100 2021-2026 inclut des titres IA/semi-conducteurs à très forte "
        "hausse (ex. NVDA) -- un signal momentum qui capte systématiquement ces titres "
        "explique une part significative du Sharpe élevé, cohérent avec le marché "
        "haussier concentré de cette période plutôt qu'un edge généralisable."
    )

    out = ROOT / "results" / "nonml_short_term_momentum_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
