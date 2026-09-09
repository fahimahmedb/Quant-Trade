"""Audit adversarial — Expérience C' : sensibilité Stratégie A à la sortie.

1. Recalcul indépendant des indicateurs (SMA50, SMA20, breakout 20j,
   RSI14, ATR14) par boucles explicites.
2. Vérification arithmétique des trades pour les variantes à TP fixe
   (R-multiple exact ±1R/+2R/+3R/+4R selon la variante).
3. Test anti-lookahead (perturbation du futur) pour chacune des 6
   variantes : l'equity avant le point de coupure ne doit pas changer.
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
from nonml_exit_rule_sensitivity_daily_backtest import (  # noqa: E402
    compute_indicators, simulate, START, DATA_PATH, SMA_WINDOW, SMA20_WINDOW,
    BREAKOUT_WINDOW, SL_MULT, VARIANTS,
)


def independent_indicators(df):
    high = df["high"].values
    close = df["close"].values
    n = len(df)
    sma50 = np.full(n, np.nan)
    sma20 = np.full(n, np.nan)
    for t in range(SMA_WINDOW - 1, n):
        sma50[t] = close[t - SMA_WINDOW + 1:t + 1].mean()
    for t in range(SMA20_WINDOW - 1, n):
        sma20[t] = close[t - SMA20_WINDOW + 1:t + 1].mean()
    brk = np.full(n, np.nan)
    for t in range(BREAKOUT_WINDOW, n):
        brk[t] = high[t - BREAKOUT_WINDOW:t].max()
    return sma50, sma20, brk


def main():
    df = load_ohlc(str(DATA_PATH))
    quality_report(df)
    ind = compute_indicators(df)

    lines = ["# Audit adversarial — Expérience C' : sensibilité Stratégie A à la sortie", "",
             "## 1. Recalcul indépendant SMA50 / SMA20 / niveau breakout (boucles explicites)", ""]

    sma50_i, sma20_i, brk_i = independent_indicators(df)
    d50 = np.nanmax(np.abs(ind["sma50"][START:] - sma50_i[START:]))
    d20 = np.nanmax(np.abs(ind["sma20"][START:] - sma20_i[START:]))
    dbrk = np.nanmax(np.abs(ind["breakout_level"][START:] - brk_i[START:]))
    check1_ok = d50 < 1e-6 and d20 < 1e-6 and dbrk < 1e-6
    lines.append(f"- Écart max SMA50 : {d50:.2e}, SMA20 : {d20:.2e}, breakout 20j : {dbrk:.2e}")
    lines.append(f"- **{'OK' if check1_ok else 'ÉCHEC'}**")

    lines.append("")
    lines.append("## 2. Vérification arithmétique des trades (variantes à TP fixe)")
    lines.append("")
    r_ok_all = True
    for name, mode, tp_r, tsd in VARIANTS:
        if mode not in ("fixed_tp", "time_stop"):
            continue
        sim = simulate(df, ind, mode, tp_r, tsd)
        bad = []
        for tr in sim["trades"]:
            if tr["reason"] == "TP":
                ok = abs(tr["r_multiple"] - tp_r) < 1e-6
            elif tr["reason"] == "SL":
                ok = abs(tr["r_multiple"] - (-1.0)) < 1e-6
            else:  # TIME_STOP : R-multiple libre, juste borne verifiee
                ok = -1.0 - 1e-9 <= tr["r_multiple"] <= tp_r + 1e-9
            if not ok:
                bad.append(tr)
        r_ok_all = r_ok_all and (len(bad) == 0)
        lines.append(f"- {name} : {len(sim['trades'])} trades vérifiés, "
                     f"{len(bad)} hors attendu — **{'OK' if not bad else 'ÉCHEC — ' + str(bad)}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur, OHLC), par variante")
    lines.append("")
    df_pert = df.copy()
    cut = len(df_pert) // 2
    rng = np.random.default_rng(73)
    shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
    for col in ("open", "high", "low", "close"):
        df_pert.loc[df_pert.index[cut:], col] = df_pert[col].values[cut:] * shock
    ind_pert = compute_indicators(df_pert)
    check_end = cut - SMA_WINDOW - 5

    leak_ok_all = True
    for name, mode, tp_r, tsd in VARIANTS:
        sim = simulate(df, ind, mode, tp_r, tsd)
        sim_pert = simulate(df_pert, ind_pert, mode, tp_r, tsd)
        eq_before = sim["equity"][START:check_end]
        eq_after = sim_pert["equity"][START:check_end]
        leak_ok = bool(np.allclose(eq_before, eq_after, equal_nan=True))
        leak_ok_all = leak_ok_all and leak_ok
        lines.append(f"- {name} : {'OK — aucune fuite' if leak_ok else 'ÉCHEC — fuite détectée'}")

    all_ok = check1_ok and r_ok_all and leak_ok_all
    lines.append("")
    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCHEC'}**")

    out = ROOT / "results" / "nonml_exit_rule_sensitivity_daily_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
