"""Audit adversarial — Overlay levé après un gap d'ouverture extrême.

Recalcul indépendant de la position (boucle event-driven explicite,
indépendante de la boucle du backtest) et test anti-lookahead
(perturbation du futur, y compris des prix d'ouverture).
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
from nonml_gap_overlay_backtest import gap_position, GAP_THRESHOLD, WINDOW_LEN, CAP, MARKETS  # noqa: E402


def independent_gap_position(open_: np.ndarray, close: np.ndarray) -> np.ndarray:
    T = len(close)
    pos = np.ones(T)
    countdown = 0
    for t in range(1, T):
        gap_t = open_[t] / close[t - 1] - 1.0
        if abs(gap_t) >= GAP_THRESHOLD:
            countdown = WINDOW_LEN
        if countdown > 0:
            pos[t] = CAP
            countdown -= 1
    return pos[:-1]


def main():
    lines = ["# Audit adversarial — Overlay levé après un gap d'ouverture extrême", "",
             "## 1. Recalcul indépendant (boucle event-driven vs boucle du backtest)", "",
             "| Marché | Écart position (nb j.) | %j levé |",
             "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        open_ = df["open"].values
        close = df["close"].values
        pos_orig = gap_position(open_, close)
        pos_indep = independent_gap_position(open_, close)
        diff = int(np.sum(pos_orig != pos_indep))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} | {100*(pos_orig > 1.0).mean():.1f}% |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur, close ET open)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        open_ = df["open"].values
        close = df["close"].values
        pos_before = gap_position(open_, close)

        cut = len(close) // 2
        rng = np.random.default_rng(71)
        close_pert = close.copy()
        open_pert = open_.copy()
        shock = rng.normal(0, 0.1, len(close) - cut)
        close_pert[cut:] = close_pert[cut:] * (1.0 + shock)
        open_pert[cut:] = open_pert[cut:] * (1.0 + shock)
        pos_after = gap_position(open_pert, close_pert)

        check_end = cut - WINDOW_LEN
        identical = bool(np.array_equal(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : le gap d'ouverture extrême (≥2%) est un "
                 "événement rare (0,4% à 7,5% du temps levé selon le marché) et, comme les "
                 "chocs de clôture-à-clôture déjà testés (#22/#24), il coïncide souvent avec le "
                 "début d'un mouvement de marché qui se poursuit plutôt qu'un point de rebond "
                 "fiable -- confirme que le timing basé sur un choc ponctuel (quelle que soit sa "
                 "définition précise : clôture ou ouverture) ne constitue pas un signal de levier "
                 "exploitable dans ce cadre.")

    out = ROOT / "results" / "nonml_gap_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
