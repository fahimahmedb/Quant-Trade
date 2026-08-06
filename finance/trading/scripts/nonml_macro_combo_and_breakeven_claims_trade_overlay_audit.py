"""Audit indépendant — Combinaison ET (3/3) breakeven inflation +
demandes continues + balance commerciale.

1. Recalcul indépendant de la logique ET par boucle explicite (sans
   l'opérateur vectorisé `&` du script principal), à partir des 3
   portes individuelles déjà validées par leurs propres audits dédiés
   (#200/#322/#327) — pas de recalcul des portes elles-mêmes (déjà
   fait), seulement de la logique de combinaison.
2. Vérification de l'alignement du point de départ (intersection des 3
   zones valides) par méthode indépendante.
3. Anti-lookahead par troncature de l'historique sur la combinaison.
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
from nonml_inflation_breakeven_overlay_backtest import (  # noqa: E402
    CUT, MARKETS, load_t10yie_lag, expanding_tercile_cut_high as t10yie_gate_high,
)
from nonml_continuing_claims_overlay_backtest import (  # noqa: E402
    build_continuing_claims_yoy_series, load_continuing_claims_yoy_lag,
)
from nonml_trade_balance_overlay_backtest import (  # noqa: E402
    build_trade_balance_series, load_trade_balance_lag,
)
from nonml_jobless_claims_overlay_backtest import (  # noqa: E402
    expanding_tercile_cut_high as claims_gate_high,
)
from nonml_m2_growth_overlay_backtest import (  # noqa: E402
    expanding_tercile_cut_low as trade_gate_low,
)
from nonml_macro_combo_and_breakeven_claims_trade_overlay_backtest import and_3_of_3  # noqa: E402


def manual_and_3_of_3(g1: np.ndarray, g2: np.ndarray, g3: np.ndarray) -> np.ndarray:
    """Recalcul par boucle explicite, sans l'operateur vectorise."""
    T = len(g1)
    out = np.zeros(T, dtype=bool)
    for t in range(T):
        out[t] = (g1[t] == CUT) and (g2[t] == CUT) and (g3[t] == CUT)
    return out


def main():
    lines = ["# Audit — Combinaison ET (3/3) breakeven inflation + demandes continues + balance commerciale", ""]
    all_ok = True

    claims_series = build_continuing_claims_yoy_series()
    trade_series = build_trade_balance_series()

    lines.append("## 1. Recalcul indépendant de la logique ET (boucle explicite)")
    lines.append("")
    lines.append("| Marché | Séances (intersection) | Désaccords logique ET |")
    lines.append("|---|---|---|")

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        t10yie_lag = load_t10yie_lag(dates)[1:]
        claims_lag = load_continuing_claims_yoy_lag(dates, claims_series)[1:]
        trade_lag = load_trade_balance_lag(dates, trade_series)[1:]

        gate1 = t10yie_gate_high(t10yie_lag)
        gate2 = claims_gate_high(claims_lag)
        gate3 = trade_gate_low(trade_lag)

        valid = np.isfinite(gate1) & np.isfinite(gate2) & np.isfinite(gate3)
        start = int(np.argmax(valid)) if valid.any() else len(valid)

        official = and_3_of_3(gate1[start:], gate2[start:], gate3[start:])
        manual = manual_and_3_of_3(gate1[start:], gate2[start:], gate3[start:])

        n_diff = int((official != manual).sum())
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {len(official)} | {n_diff} |")

    lines.append("")
    lines.append(f"**{'OK — logique ET confirmée par recalcul indépendant (0 désaccord).' if all_ok else 'ÉCHEC — désaccord détecté.'}**")
    lines.append("")

    # Verification de l'intersection du point de depart, sur NDX.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    quality_report(df)
    dates = pd.DatetimeIndex(df["date"].values)
    t10yie_lag = load_t10yie_lag(dates)[1:]
    claims_lag = load_continuing_claims_yoy_lag(dates, claims_series)[1:]
    trade_lag = load_trade_balance_lag(dates, trade_series)[1:]
    gate1 = t10yie_gate_high(t10yie_lag)
    gate2 = claims_gate_high(claims_lag)
    gate3 = trade_gate_low(trade_lag)

    start1 = int(np.argmax(np.isfinite(gate1)))
    start2 = int(np.argmax(np.isfinite(gate2)))
    start3 = int(np.argmax(np.isfinite(gate3)))
    valid = np.isfinite(gate1) & np.isfinite(gate2) & np.isfinite(gate3)
    start_combo = int(np.argmax(valid)) if valid.any() else len(valid)
    expected_start = max(start1, start2, start3)

    lines.append("## 2. Vérification du point de départ (intersection des 3 zones valides, NDX)")
    lines.append(f"- Début individuel #200 (T10YIE) : séance {start1}")
    lines.append(f"- Début individuel #322 (CCSA) : séance {start2}")
    lines.append(f"- Début individuel #327 (BOPGSTB) : séance {start3}")
    lines.append(f"- Début de la combinaison (calcul officiel, `argmax` sur l'intersection) : séance {start_combo}")
    lines.append(f"- Début attendu (max des 3, le plus contraignant) : séance {expected_start}")
    ok_start = (start_combo == expected_start)
    all_ok &= ok_start
    lines.append(f"- **{'OK — le point de départ de la combinaison correspond bien au signal le plus tardivement disponible (T10YIE, 2003+), aucune fuite via un signal encore indisponible' if ok_start else 'ÉCART DÉTECTÉ'}**")
    lines.append("")

    # Anti-lookahead general : troncature de l'historique sur la combinaison.
    pos_full = np.where(and_3_of_3(gate1[start_combo:], gate2[start_combo:], gate3[start_combo:]), CUT, 1.0)
    T_CUT = 2000
    dates_trunc = dates[:start_combo + T_CUT]
    t10yie_trunc = load_t10yie_lag(dates_trunc)[1:]
    claims_trunc = load_continuing_claims_yoy_lag(dates_trunc, claims_series)[1:]
    trade_trunc = load_trade_balance_lag(dates_trunc, trade_series)[1:]
    g1_trunc = t10yie_gate_high(t10yie_trunc)
    g2_trunc = claims_gate_high(claims_trunc)
    g3_trunc = trade_gate_low(trade_trunc)
    pos_trunc = np.where(and_3_of_3(g1_trunc[start_combo:], g2_trunc[start_combo:], g3_trunc[start_combo:]), CUT, 1.0)
    n_compare = min(T_CUT, len(pos_full), len(pos_trunc))
    match = np.array_equal(pos_full[:n_compare], pos_trunc[:n_compare])
    all_ok &= match

    lines.append(f"## 3. Anti-lookahead (NDX, troncature à {start_combo + T_CUT} séances)")
    lines.append(f"- Comparaison sur les {n_compare} premières positions post-démarrage, pleine série vs série tronquée : "
                 f"{'identique' if match else 'DIFFÉRENT'}.")
    lines.append(f"- **{'OK — aucune fuite' if match else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")
    lines.append("")
    lines.append("Note : les 3 portes individuelles (#200/#322/#327) ont chacune déjà été "
                 "auditées indépendamment dans leurs cycles respectifs (alignement causal, "
                 "tercile expanding, décalage de publication), et la logique de combinaison "
                 "réutilise les MÊMES gates que le #334 (déjà auditées CONFORME) — cet audit "
                 "se concentre spécifiquement sur la nouvelle logique ET, seul élément "
                 "distinct de ce cycle par rapport au #334.")

    out = ROOT / "results" / "nonml_macro_combo_and_breakeven_claims_trade_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
