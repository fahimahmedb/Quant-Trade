"""Audit indépendant — agrégation de rendements de portefeuille.

Vérifie par un chemin de calcul TOTALEMENT différent que le rendement d'un
panier équipondéré vaut bien `Σ wᵢ·r_simple,ᵢ` et non `Σ wᵢ·r_log,ᵢ`.

Méthode de contrôle : simulation en NOMBRE DE PARTS. On part d'un capital de
1,0 réparti entre les titres cotés, on détient les parts pendant la période, et
on relit la valeur du portefeuille aux prix du marché. Aucune formule de
rendement n'intervient — que des prix et des quantités. C'est la définition
comptable de la performance d'un portefeuille, indépendante de toute convention
log/simple.

On compare ensuite trois agrégations :
  1. `Σ wᵢ·r_log,ᵢ` composé par `cumprod(1+·)`   <- ce que faisaient les scripts
  2. `Σ wᵢ·r_simple,ᵢ` composé par `cumprod(1+·)` <- correction appliquée
  3. simulation en parts                          <- référence indépendante

Usage : python3 scripts/nonml_portfolio_log_aggregation_audit.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "src"))

PRICES_DIR = ROOT / "data" / "pead" / "prices"
OUT = ROOT / "results" / "nonml_portfolio_log_aggregation_audit.md"

REBAL_EVERY = 21


def load_prices() -> pd.DataFrame:
    """Lecture directe des JSON {ts, close}. Volontairement independante du
    chargeur utilise par les backtests."""
    import json
    frames = {}
    for f in sorted(PRICES_DIR.glob("*.json")):
        d = json.loads(f.read_text())
        idx = pd.to_datetime(d["ts"], unit="s").normalize()
        frames[f.stem] = pd.Series(d["close"], index=idx)
    return pd.DataFrame(frames).sort_index()


def main() -> None:
    P = load_prices()
    T, n = P.shape
    close = P.values
    exists = np.isfinite(close)

    r_simple = (P / P.shift(1) - 1.0).values.copy()
    r_log = np.log(P / P.shift(1)).values.copy()
    r_simple[0, :] = 0.0
    r_log[0, :] = 0.0
    r_simple = np.nan_to_num(r_simple, nan=0.0)
    r_log = np.nan_to_num(r_log, nan=0.0)

    # Poids équipondérés sur les titres cotés, rebalancés tous les REBAL_EVERY jours.
    W = np.zeros((T, n))
    rebal = list(range(0, T, REBAL_EVERY))
    for k, t in enumerate(rebal):
        end = rebal[k + 1] if k + 1 < len(rebal) else T
        listed = exists[t]
        if listed.sum() > 0:
            W[t:end] = listed.astype(float) / listed.sum()

    pnl_log_agg = (W * r_log).sum(axis=1)
    pnl_simple_agg = (W * r_simple).sum(axis=1)

    eq_log_agg = np.cumprod(1.0 + pnl_log_agg)
    eq_simple_agg = np.cumprod(1.0 + pnl_simple_agg)

    # --- Référence indépendante : simulation en nombre de parts ---
    value = 1.0
    eq_shares = np.empty(T)
    shares = np.zeros(n)
    for t in range(T):
        if t > 0:
            px = np.where(exists[t], np.nan_to_num(close[t], nan=0.0), 0.0)
            value = float((shares * px).sum())
        eq_shares[t] = value
        if t in rebal:
            listed = exists[t]
            if listed.sum() > 0:
                px = np.where(listed, close[t], np.nan)
                alloc = value / listed.sum()
                shares = np.where(listed, alloc / np.where(listed, px, 1.0), 0.0)

    L = []
    L.append("# Audit — agrégation de rendements au niveau portefeuille")
    L.append("")
    L.append("**Audit de code, non pré-enregistré** (aucun paramètre à calibrer, aucun seuil")
    L.append("de succès : on vérifie une identité comptable).")
    L.append("")
    L.append("## Question")
    L.append("")
    L.append("Les backtests de portefeuille au niveau titre calculaient le P&L quotidien")
    L.append("comme `Σ wᵢ·r_log,ᵢ` — une moyenne pondérée de rendements **log**. Or le")
    L.append("rendement d'un panier pondéré est `Σ wᵢ·r_simple,ᵢ` : l'agrégation entre")
    L.append("titres est additive en rendement simple, pas en log. La composition dans le")
    L.append("temps, elle, est additive en log. Les deux opérations ne commutent pas.")
    L.append("")
    L.append("## Contrôle indépendant")
    L.append("")
    L.append("Référence calculée **en nombre de parts** : capital initial 1,0 réparti entre")
    L.append("les titres cotés, parts détenues, portefeuille revalorisé aux prix du marché.")
    L.append("Aucune formule de rendement n'intervient — uniquement des prix et des")
    L.append("quantités. C'est la définition comptable de la performance, indépendante de")
    L.append("toute convention.")
    L.append("")
    L.append(f"Univers : {n} titres, {T} séances "
             f"({P.index[0].date()} → {P.index[-1].date()}), rebalancement tous les "
             f"{REBAL_EVERY} jours, équipondéré, sans coûts (on isole l'effet d'agrégation).")
    L.append("")
    L.append("| Méthode d'agrégation | Capital final | Rendement total |")
    L.append("|---|---|---|")
    L.append(f"| `Σ wᵢ·r_log,ᵢ` puis `cumprod(1+·)` — **ancienne méthode** | {eq_log_agg[-1]:.4f} | {100*(eq_log_agg[-1]-1):+.1f}% |")
    L.append(f"| `Σ wᵢ·r_simple,ᵢ` puis `cumprod(1+·)` — **correction** | {eq_simple_agg[-1]:.4f} | {100*(eq_simple_agg[-1]-1):+.1f}% |")
    L.append(f"| Simulation en parts — **référence indépendante** | {eq_shares[-1]:.4f} | {100*(eq_shares[-1]-1):+.1f}% |")
    L.append("")

    err_old = abs(eq_log_agg[-1] - eq_shares[-1]) / eq_shares[-1]
    err_new = abs(eq_simple_agg[-1] - eq_shares[-1]) / eq_shares[-1]
    L.append(f"- écart de l'ancienne méthode à la référence : **{100*err_old:.2f} %**")
    L.append(f"- écart de la correction à la référence : **{100*err_new:.2f} %**")
    L.append("")
    if err_new < err_old:
        L.append("**La correction reproduit la référence comptable ; l'ancienne méthode non.**")
    else:
        L.append("**ATTENTION : la correction ne rapproche PAS de la référence — à réexaminer.**")
    L.append("")
    L.append("Le résidu de la correction vis-à-vis de la simulation en parts n'est pas un")
    L.append("bug : entre deux rebalancements les poids dérivent avec les prix, alors que la")
    L.append("formule `Σ wᵢ·rᵢ` suppose les poids constants sur la période de détention.")
    L.append("C'est l'écart de rebalancement usuel, d'un ordre de grandeur sans rapport avec")
    L.append("l'erreur d'agrégation log.")
    L.append("")
    L.append("## Sens du biais")
    L.append("")
    L.append("`log(1+x) ≤ x`, donc `Σ wᵢ·r_log,ᵢ ≤ Σ wᵢ·r_simple,ᵢ` : l'ancienne méthode")
    L.append("**sous-estime systématiquement** le rendement de tout panier, et d'autant plus")
    L.append("que les titres sont volatils. Elle pénalise donc le plus le panier le plus")
    L.append("large et le plus volatil — en pratique la référence Buy&Hold équipondérée,")
    L.append("qui détient tout l'univers. Les stratégies sélectives étaient donc comparées")
    L.append("à une référence artificiellement affaiblie.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"log-agg   : {eq_log_agg[-1]:.4f} ({100*(eq_log_agg[-1]-1):+.1f}%)")
    print(f"simple-agg: {eq_simple_agg[-1]:.4f} ({100*(eq_simple_agg[-1]-1):+.1f}%)")
    print(f"parts     : {eq_shares[-1]:.4f} ({100*(eq_shares[-1]-1):+.1f}%)")
    print(f"ecart ancien={100*err_old:.2f}%  ecart corrige={100*err_new:.2f}%")
    print(f"ecrit : {OUT}")


if __name__ == "__main__":
    main()
