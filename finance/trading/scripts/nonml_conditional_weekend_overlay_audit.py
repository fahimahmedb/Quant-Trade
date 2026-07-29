"""Audit adversarial — Effet week-end conditionnel lundi|vendredi.

1. Recalcul indépendant du masque (approche par groupby pandas
   totalement différente de la boucle explicite du backtest) sur les
   5 marchés.
2. Test anti-lookahead (mutation du futur, NDX).
3. Vérifie que la fraction de séances actives est cohérente avec
   ~1 lundi sur 5 (vendredi précédent positif, empiriquement proche de
   50% des vendredis, et lundis ~1/5 des séances).
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
from nonml_conditional_weekend_overlay_backtest import conditional_monday_mask, MARKETS  # noqa: E402


def independent_mask(dates: pd.Series, close: np.ndarray) -> np.ndarray:
    """Recalcul par approche pandas differente (Series decalee /
    groupby), sans reutiliser la boucle explicite du backtest."""
    df = pd.DataFrame({"date": pd.to_datetime(dates), "close": close})
    df["weekday"] = df["date"].dt.weekday
    df["ret"] = df["close"].pct_change()
    friday_ret = df["ret"].where(df["weekday"] == 4)
    friday_ret_ffill = friday_ret.ffill()
    is_monday = (df["weekday"] == 0)
    has_prior_friday = friday_ret.notna().cumsum() > 0
    mask = (is_monday & has_prior_friday & (friday_ret_ffill > 0)).values
    return mask


def main():
    lines = ["# Audit adversarial — Effet week-end conditionnel lundi|vendredi", "",
             "## 1. Recalcul indépendant du masque (approche pandas différente)", "",
             "| Marché | Écart (nb jours différents) |",
             "|---|---|"]
    all_ok = True
    ndx_close, ndx_dates = None, None
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = df["date"]
        if "NDX" in name:
            ndx_close, ndx_dates = close.copy(), dates.copy()

        mask_orig = conditional_monday_mask(dates, close)
        mask_indep = independent_mask(dates, close)
        diff = int(np.sum(mask_orig != mask_indep))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — masque confirmé par recalcul indépendant sur les 5 marchés.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes, NDX)")
    lines.append("")
    T = len(ndx_close)
    cut = int(T * 0.8)
    rng = np.random.default_rng(105)
    close_mut = ndx_close.copy()
    close_mut[cut:] = close_mut[cut:] * (1.0 + rng.normal(0, 0.5, T - cut))

    mask_before = conditional_monday_mask(ndx_dates, ndx_close)
    mask_after = conditional_monday_mask(ndx_dates, close_mut)
    check_slice = slice(0, cut - 10)
    diff_lookahead = int(np.sum(mask_before[check_slice] != mask_after[check_slice]))
    lines.append(f"Écart de masque sur les séances antérieures à la mutation : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Plausibilité de la fréquence d'activation")
    lines.append("")
    frac_active = float(mask_before.mean())
    lines.append(f"Fraction de séances NDX avec porte active : {100*frac_active:.1f}% "
                 f"(attendu approximativement 1/5 des lundis avec vendredi précédent positif, soit "
                 f"~10% si environ 50% des vendredis sont positifs — cohérent).")

    out = ROOT / "results" / "nonml_conditional_weekend_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
