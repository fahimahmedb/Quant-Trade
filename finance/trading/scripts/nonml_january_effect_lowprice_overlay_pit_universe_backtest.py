"""Backtest — effet janvier (proxy prix bas) en overlay, univers de titres
POINT-IN-TIME (spécification pré-enregistrée dans
`PREREG_january_effect_lowprice_overlay_pit_universe.md`, committée avant ce
script).

Réutilisation stricte (Règle 7) du cycle d'origine
(`nonml_january_effect_lowprice_overlay_backtest.py`) : **aucun paramètre
modifié**. Seul l'univers change — `data/pead/prices/` (liste NDX-100 de 2026,
biaisée par le survivant) devient `data/pead/prices_pit/`, avec appartenance
résolue à chaque date par `ndx100_membership.tickers_as_of_date`.

Contrairement au cycle #396 (P&L indiciel), **ce candidat est un portefeuille** :
le biais du survivant agit directement sur la mesure de performance.

Limite héritée, inchangée : le prix de clôture sert de proxy de taille faute de
capitalisation boursière. Un prix bas n'est pas une petite capitalisation.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
COMPOSITION_START = pd.Timestamp("2015-01-01")

# --- Parametres REPRIS A L'IDENTIQUE du cycle d'origine (Regle 7) ---
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0


def load_prices_pit():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > REBAL_EVERY + 1:
            series[path.stem] = close
    return series


def lag_one_day(W):
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def main():
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()

    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T = len(P)
    tickers = list(P.columns)
    n_tickers = len(tickers)

    # Rendements SIMPLES par titre (correction #378-#380) : le rendement d'un
    # panier pondere est somme(w_i * r_simple_i).
    R = (P / P.shift(1) - 1.0)
    R.iloc[0, :] = 0.0
    close = P.values
    exists = np.isfinite(close)

    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowprice = np.zeros((T, n_tickers))
    # `investable` marque les dates ou l'appartenance PIT est definie ET ou au
    # moins un titre membre est cote. Sans ce masque explicite, la fenetre
    # testable demarrerait en 1985 avec des poids nuls (piege rencontre au #396).
    investable = np.zeros(T, dtype=bool)
    coverage = []

    start = REBAL_EVERY
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        if P.index[t] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        c = close[t]
        elig = np.where(np.isfinite(c) & exists[t] & member_cols)[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(c[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowprice[t:end] = w
            investable[t:end] = True
            coverage.append(len(elig) / max(1, len(members)))

    is_january = np.array([d.month == 1 for d in P.index])
    exposure = np.where(is_january, CAP, 1.0)

    weights_base = weights_lowprice
    weights_lev = weights_lowprice * exposure[:, None]
    weights_base = lag_one_day(weights_base)
    weights_lev = lag_one_day(weights_lev)
    is_january = np.concatenate(([False], is_january[:-1]))
    investable = np.concatenate(([False], investable[:-1]))

    first = int(np.argmax(investable)) if investable.any() else T
    start_eff = max(start, first)

    R_safe = np.nan_to_num(R.values, nan=0.0)
    pnl_base = (weights_base[start_eff:] * R_safe[start_eff:]).sum(axis=1)
    pnl_lev = (weights_lev[start_eff:] * R_safe[start_eff:]).sum(axis=1)

    turn_base = np.abs(np.diff(weights_base[start_eff:], axis=0,
                               prepend=weights_base[start_eff:start_eff + 1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(weights_lev[start_eff:], axis=0,
                              prepend=weights_lev[start_eff:start_eff + 1])).sum(axis=1) / 2.0
    pnl_gross_base, pnl_gross_lev = pnl_base.copy(), pnl_lev.copy()
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)

    me_base = trading_metrics(np.log1p(pnl_base))
    me_lev = trading_metrics(np.log1p(pnl_lev))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    verdict = sharpe_ok and ret_ok

    n_jan = int(is_january[start_eff:].sum())
    n_tot = T - start_eff
    cov = float(np.mean(coverage)) if coverage else float("nan")

    lines = [
        "# Résultat — Effet janvier (proxy prix bas) en overlay, univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine : **aucun paramètre modifié**. "
        "Seul l'univers change — appartenance NDX-100 résolue à chaque date "
        "(`tickers_as_of_date`) au lieu de la liste 2026 appliquée rétroactivement.",
        "",
        f"Univers PIT : {n_tickers} tickers disponibles, couverture moyenne "
        f"(éligibles / membres réels) : {100*cov:.1f}%. "
        f"{n_tot} séances testables ({P.index[start_eff].date()} → {P.index[-1].date()}), "
        f"rebalancement tous les {REBAL_EVERY}j, tercile au prix de clôture le plus faible.",
        "",
        f"Overlay janvier actif {100*n_jan/max(1, n_tot):.1f}% du temps (CAP {CAP}x).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Tercile prix bas 1.0x (référence) | {me_base['sharpe_ann']:+.2f} | "
        f"{100*ret_base:+.1f}% | {me_base['max_drawdown_pct']:.1f}% |",
        f"| **Tercile prix bas + overlay janvier {CAP}x** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
    ]
    if verdict:
        lines.append("**PASS — critère renforcé (Sharpe ET rendement) atteint sur univers point-in-time.**")
    else:
        lines.append("**FAIL — critère renforcé (Sharpe ET rendement) NON atteint sur univers point-in-time.**")
    lines.append("")
    lines.append("**Limite héritée, inchangée :** le prix de clôture sert de proxy de taille "
                 "faute de capitalisation boursière disponible. Un prix bas n'est pas une "
                 "petite capitalisation — le portage sur univers point-in-time ne corrige "
                 "pas cette limite et ne prétend pas le faire.")
    lines.append("")
    lines.append("Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. "
                 "Leur comparaison mesure l'effet du biais du survivant sur ce candidat.")
    lines.append("")

    out = ROOT / "results" / "nonml_january_effect_lowprice_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(ROOT / "results" / "nonml_january_effect_lowprice_overlay_pit_universe_pnl.npz",
             pnl_gross_ov=pnl_gross_lev, pnl_gross_bh=pnl_gross_base,
             turn_ov=turn_lev, turn_bh=turn_base,
             dates=np.asarray(P.index)[start_eff:], cost_bps=COST_BPS)

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
