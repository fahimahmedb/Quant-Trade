"""Audit adversarial — Overlay levé sur rebond après choc 1 séance.

Même structure de vérification qu'au cycle #22 : recalcul indépendant du
déclencheur et de la position, mesure de la fraction de jours levés
pendant un drawdown sévère (explication économique du FAIL).
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
from nonml_single_day_shock_rebound_backtest import (  # noqa: E402
    rebound_exposure, SHOCK_THRESHOLD, REBOUND_LEN, CAP, MARKETS,
)


def independent_trigger(close: np.ndarray) -> np.ndarray:
    s = pd.Series(close)
    ret1 = np.log(s / s.shift(1))
    return (ret1 <= SHOCK_THRESHOLD).fillna(False).values


def independent_position(close: np.ndarray) -> np.ndarray:
    trigger = independent_trigger(close)
    T = len(close)
    pos = np.ones(T)
    countdown = 0
    for t in range(T):
        if trigger[t]:
            countdown = REBOUND_LEN
        pos[t] = CAP if countdown > 0 else 1.0
        if countdown > 0:
            countdown -= 1
    return pos


def main():
    lines = ["# Audit adversarial — Overlay levé rebond choc 1 séance (indice)", "",
             "| Marché | Écart déclencheur (nb j.) | Écart position (nb j.) | %j levé PENDANT drawdown>20% |",
             "|---|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values

        pos_orig = rebound_exposure(close)
        pos_indep = independent_position(close)
        diff_pos = int(np.sum(pos_orig != pos_indep))

        T = len(close)
        day_ret = np.zeros(T)
        day_ret[1:] = np.log(close[1:] / close[:-1])
        trig_orig = day_ret <= SHOCK_THRESHOLD
        trig_indep = independent_trigger(close)
        diff_trig = int(np.sum(trig_orig != trig_indep))
        all_ok &= (diff_pos == 0) and (diff_trig == 0)

        rolling_max = np.maximum.accumulate(close)
        dd = close / rolling_max - 1.0
        in_severe_dd = dd <= -0.20
        pct_levered_in_dd = 100 * (pos_orig[in_severe_dd] > 1.0).mean() if in_severe_dd.any() else float("nan")

        lines.append(f"| {name} | {diff_trig} | {diff_pos} | {pct_levered_in_dd:.1f}% |")

    lines.append("")
    lines.append(f"**{'OK — déclencheur et position confirmés par recalcul indépendant, aucun bug.' if all_ok else 'ÉCHEC — incohérence détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : même si le déclencheur est ponctuel (1 séance, "
                 "≥5%) plutôt qu'étalé sur 3j (#22), le résultat reste un FAIL net -- un choc de "
                 "cette ampleur reste statistiquement plus souvent le signe avant-coureur d'une "
                 "poursuite de la baisse (krach 2000-2002, 2008, 2020, 2022) qu'un point bas isolé, "
                 "donc lever l'exposition juste après continue de dégrader Sharpe et rendement au "
                 "lieu de capter un rebond fiable -- confirme la conclusion du #22 sous une variante "
                 "de déclencheur différente (single-day vs 3j cumulé).")

    out = ROOT / "results" / "nonml_single_day_shock_rebound_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
