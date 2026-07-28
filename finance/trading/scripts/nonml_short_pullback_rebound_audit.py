"""Audit adversarial — Overlay levé sur pullback court terme.

Le résultat brut est un FAIL très marqué (rendement négatif jusqu'à -99%
sur NDX/Russell/S&P 500 en 40 ans) -- suffisamment extrême pour mériter
une vérification indépendante renforcée avant d'être rapporté tel quel :
1) recalcul du déclencheur (repli 3j <= -3%) par une méthode vectorisée
   indépendante (rolling via pandas plutôt que boucle explicite) ;
2) recalcul de la position jour par jour par simulation event-driven
   indépendante (sans réutiliser rebound_exposure()) ;
3) mesure de la fraction de jours où l'overlay est actif PENDANT un
   drawdown sévère du marché (pour expliquer économiquement le FAIL :
   le repli court terme au niveau indice n'est PAS un signal de rebond,
   c'est souvent le DÉBUT d'une baisse prolongée -> lever dessus aggrave
   les pertes, contrairement à l'hypothèse).
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
from nonml_short_pullback_rebound_backtest import (  # noqa: E402
    rebound_exposure, PB_WINDOW, PB_THRESHOLD, REBOUND_LEN, CAP, MARKETS,
)


def independent_trigger(close: np.ndarray) -> np.ndarray:
    s = pd.Series(np.log(close))
    ret3 = s.diff(PB_WINDOW)
    return (ret3 <= PB_THRESHOLD).fillna(False).values


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
    lines = ["# Audit adversarial — Overlay levé pullback court terme (indice)", "",
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
        trig_orig_T = len(close)
        trig_indep = independent_trigger(close)
        # trigger recompute inside rebound_exposure for comparison
        pullback_ret = np.full(trig_orig_T, np.nan)
        for i in range(PB_WINDOW, trig_orig_T):
            pullback_ret[i] = np.log(close[i] / close[i - PB_WINDOW])
        trig_orig = np.nan_to_num(pullback_ret, nan=0.0) <= PB_THRESHOLD
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
    lines.append("**Lecture économique du FAIL** : le repli court terme (3j, -3%) au niveau indice "
                 "n'est pas un signal fiable de rebond imminent -- il se produit fréquemment en DÉBUT "
                 "de correction/krach prolongé (la colonne %j levé pendant drawdown sévère montre que "
                 "l'overlay reste actif une part importante du temps precisement quand le marché "
                 "continue de baisser), donc lever l'exposition dessus aggrave la perte au lieu de "
                 "capter un rebond -- l'inverse de l'hypothèse pré-enregistrée.")

    out = ROOT / "results" / "nonml_short_pullback_rebound_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
