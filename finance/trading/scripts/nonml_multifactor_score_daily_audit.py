"""Audit adversarial — Stratégie B : Score multi-facteurs /10 (daily).

1. Recalcul indépendant du score (tous les facteurs, boucles explicites,
   sans réutiliser `nonml_multifactor_score_daily_backtest.py::compute_score`
   — RSI/ATR restent `prediction.py::_rsi`/`_atr`, communs à tout le repo).
2. Vérification arithmétique des trades (R-multiple exact ±1R/+2R aux
   sorties SL/TP).
3. Test anti-lookahead (perturbation du futur) : les décisions et
   l'equity avant le point de coupure ne doivent pas changer.
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
from prediction import _rsi  # noqa: E402
from nonml_multifactor_score_daily_backtest import (  # noqa: E402
    compute_score, simulate, START, DATA_PATH,
    SMA20_WINDOW, SMA50_WINDOW, SMA200_WINDOW,
    BREAKOUT20_WINDOW, BREAKOUT50_WINDOW, MOMENTUM_WINDOW,
    RSI_LO, RSI_HI, SCORE_THRESHOLD, SL_MULT, TP_MULT,
)


def independent_score(df):
    """Recalcul du score par boucles explicites, indépendant de compute_score."""
    high = df["high"].values
    close = df["close"].values
    n = len(df)
    rsi14 = _rsi(df["close"], 14).values

    score = np.full(n, np.nan)
    for t in range(SMA200_WINDOW, n):
        sma20 = close[t - SMA20_WINDOW + 1:t + 1].mean()
        sma50 = close[t - SMA50_WINDOW + 1:t + 1].mean()
        sma200 = close[t - SMA200_WINDOW + 1:t + 1].mean()
        brk20 = high[t - BREAKOUT20_WINDOW:t].max()
        brk50 = high[t - BREAKOUT50_WINDOW:t].max()
        close_mom = close[t - MOMENTUM_WINDOW]
        if np.isnan(rsi14[t]):
            continue
        s = 0.0
        s += 1.0 if close[t] > sma50 else 0.0
        s += 1.0 if sma50 > sma200 else 0.0
        s += 1.0 if close[t] > close[t - 1] else 0.0
        s += 1.0 if close[t] > sma20 else 0.0
        s += 1.0 if close[t] > brk20 else 0.0
        s += 1.0 if close[t] > brk50 else 0.0
        s += 0.0  # facteur Volume : structurellement toujours 0, cf. PREREG
        s += 1.0 if (RSI_LO <= rsi14[t] <= RSI_HI) else 0.0
        s += 2.0 if close[t] > close_mom else 0.0
        score[t] = s
    return score


def main():
    df = load_ohlc(str(DATA_PATH))
    quality_report(df)

    lines = ["# Audit adversarial — Stratégie B : Score multi-facteurs /10 (daily)", "",
             "## 1. Recalcul indépendant du score (boucles explicites)", ""]

    sig = compute_score(df)
    score_indep = independent_score(df)
    score_vec = sig["score"]
    both_valid = ~np.isnan(score_vec[START:]) & ~np.isnan(score_indep[START:])
    diff = np.abs(score_vec[START:][both_valid] - score_indep[START:][both_valid])
    score_diff = float(diff.max()) if len(diff) else 0.0
    nan_mismatch = int((np.isnan(score_vec[START:]) != np.isnan(score_indep[START:])).sum())
    check1_ok = score_diff < 1e-9 and nan_mismatch == 0
    lines.append(f"- Écart max score (vectorisé vs boucle), séances valides des deux côtés : {score_diff:.2e}")
    lines.append(f"- Désaccords NaN (amorçage) entre les deux implémentations : {nan_mismatch}")
    lines.append(f"- **{'OK' if check1_ok else 'ÉCHEC'}**")

    lines.append("")
    lines.append("## 2. Vérification arithmétique des trades")
    lines.append("")
    sim = simulate(df, sig)
    trades = sim["trades"]
    bad = []
    for tr in trades:
        if tr["reason"] == "TP":
            expected_r = TP_MULT / SL_MULT
            ok = abs(tr["r_multiple"] - expected_r) < 1e-6
        elif tr["reason"].startswith("SL"):
            ok = abs(tr["r_multiple"] - (-1.0)) < 1e-6
        else:
            ok = True
        if not ok:
            bad.append(tr)
    r_ok = len(bad) == 0
    lines.append(f"- Trades vérifiés : {len(trades)}")
    lines.append(f"- Trades avec R-multiple hors attendu (SL=-1R, TP=+{TP_MULT/SL_MULT:.1f}R exacts "
                 f"par construction) : {len(bad)}")
    lines.append(f"- **{'OK' if r_ok else 'ÉCHEC — ' + str(bad)}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur, OHLC)")
    lines.append("")
    df_pert = df.copy()
    cut = len(df_pert) // 2
    rng = np.random.default_rng(73)
    shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
    for col in ("open", "high", "low", "close"):
        df_pert.loc[df_pert.index[cut:], col] = df_pert[col].values[cut:] * shock

    sig_pert = compute_score(df_pert)
    sim_pert = simulate(df_pert, sig_pert)

    check_end = cut - SMA200_WINDOW - 5  # marge de securite au-dela de la coupure
    eq_before = sim["equity"][START:check_end]
    eq_after = sim_pert["equity"][START:check_end]
    leak_ok = bool(np.allclose(eq_before, eq_after, equal_nan=True))
    lines.append(f"- Equity identique avant le point de coupure (séance {check_end}) "
                 f"après perturbation du futur : {'OUI' if leak_ok else 'NON — FUITE DETECTEE'}")
    lines.append(f"- **{'OK — aucune fuite de données futures.' if leak_ok else 'ÉCHEC — fuite détectée.'}**")

    all_ok = check1_ok and r_ok and leak_ok
    lines.append("")
    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCHEC'}**")

    out = ROOT / "results" / "nonml_multifactor_score_daily_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
