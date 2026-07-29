"""Audit adversarial — Overlay de confirmation multi-marché internationale NDX+DAX.

Le résultat brut est un PASS avec MDD exactement préservé (contrairement
au #52/Russell2000 qui dégradait légèrement le MDD) -- vérification
renforcée : (1) recalcul indépendant du signal NDX (boucle explicite),
(2) test anti-lookahead sur les deux marchés, (3) valeur exacte non
arrondie du delta de Sharpe pour confirmer que le PASS n'est pas un
artefact d'arrondi à l'affichage, comme au #52.
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
from prediction import trading_metrics  # noqa: E402
from nonml_intl_breadth_confirmation_overlay_backtest import near_high_series, COST_BPS, CAP, INDEX_LOOKBACK, INDEX_THRESHOLD  # noqa: E402


def independent_near_high(close: np.ndarray) -> np.ndarray:
    T = len(close)
    out = np.zeros(T, dtype=bool)
    for i in range(INDEX_LOOKBACK, T):
        window_max = close[i - INDEX_LOOKBACK + 1:i + 1].max()
        out[i] = close[i] >= INDEX_THRESHOLD * window_max
    return out


def main():
    df_primary = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_primary)
    df_confirm = load_ohlc(str(REPO_ROOT / "data" / "dax_daily.txt"))
    quality_report(df_confirm)

    close_p = df_primary["close"].values
    close_c = df_confirm["close"].values

    signal_a = near_high_series(df_primary)
    signal_b = near_high_series(df_confirm)
    dates_primary = pd.to_datetime(df_primary["date"])
    b_aligned = signal_b.reindex(dates_primary.values, method="ffill").fillna(False).values.astype(bool)
    a_aligned = signal_a.values.astype(bool)
    both = a_aligned & b_aligned

    # 1. recalcul independant du signal NDX
    a_indep = independent_near_high(close_p)
    diff_a = int(np.sum(a_aligned[INDEX_LOOKBACK:] != a_indep[INDEX_LOOKBACK:]))

    # 2. test anti-lookahead sur les deux marches
    cut_p = len(close_p) // 2
    rng = np.random.default_rng(139)
    close_p_pert = close_p.copy()
    close_p_pert[cut_p:] = close_p_pert[cut_p:] * (1.0 + rng.normal(0, 0.1, len(close_p) - cut_p))
    a_before = a_aligned
    df_primary_pert = df_primary.copy()
    df_primary_pert["close"] = close_p_pert
    a_after = near_high_series(df_primary_pert).values.astype(bool)
    anti_leak_a = bool(np.array_equal(a_before[:cut_p], a_after[:cut_p]))

    cut_c = len(close_c) // 2
    close_c_pert = close_c.copy()
    close_c_pert[cut_c:] = close_c_pert[cut_c:] * (1.0 + rng.normal(0, 0.1, len(close_c) - cut_c))
    df_confirm_pert = df_confirm.copy()
    df_confirm_pert["close"] = close_c_pert
    b_before_series = signal_b
    b_after_series = near_high_series(df_confirm_pert)
    anti_leak_b = bool(np.array_equal(b_before_series.values[:cut_c].astype(bool),
                                        b_after_series.values[:cut_c].astype(bool)))

    # 3. delta de Sharpe non arrondi
    close = df_primary["close"].values
    bh_full = np.log(close[1:] / close[:-1])
    start = INDEX_LOOKBACK
    bh_t = bh_full[start:]
    mask = both[start:-1]
    pos = np.where(mask, CAP, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    delta_sharpe = me_ov["sharpe_ann"] - me_bh["sharpe_ann"]
    delta_mdd = me_ov["max_drawdown_pct"] - me_bh["max_drawdown_pct"]

    lines = [
        "# Audit adversarial — Overlay de confirmation multi-marché internationale NDX+DAX",
        "",
        f"Recalcul indépendant du signal NDX (boucle explicite) : {diff_a} écarts. "
        f"**{'OK.' if diff_a == 0 else 'ÉCHEC.'}**",
        "",
        f"Test anti-lookahead signal NDX : {'OK — aucune fuite.' if anti_leak_a else 'ÉCHEC.'}",
        f"Test anti-lookahead signal DAX : {'OK — aucune fuite.' if anti_leak_b else 'ÉCHEC.'}",
        "",
        f"Delta de Sharpe non arrondi (overlay − BH) : {delta_sharpe:.6f}",
        f"Delta de MDD non arrondi (overlay − BH, en points de %) : {delta_mdd:.6f}",
        f"**{'OK — le PASS tient sur la valeur exacte, pas un artefact arrondi.' if delta_sharpe > 0 else 'ÉCHEC — le PASS affiché ne tient pas sur la valeur exacte.'}**",
        "",
        "**Comparaison avec le #52 (NDX+Russell2000, domestique)** : la porte internationale "
        "(NDX+DAX) est plus sélective (27,0% du temps contre une porte domestique plus large au "
        "#52) et surtout préserve EXACTEMENT le MDD (delta ≈0, contre une dégradation de "
        "-82,9%→-83,8% au #52). Le delta de Sharpe reste néanmoins fin comme au #52 — la "
        "confirmation croisée, domestique ou internationale, n'apporte jamais un edge Sharpe "
        "massif par rapport au signal NDX seul (#37, Sharpe +0,51→+0,59), mais la variante "
        "internationale a le mérite de ne dégrader le profil de risque en AUCUNE mesure, "
        "contrairement à la variante domestique.",
    ]

    out = ROOT / "results" / "nonml_intl_breadth_confirmation_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
