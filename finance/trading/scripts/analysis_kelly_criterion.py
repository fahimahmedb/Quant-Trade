"""Analyse — Levier optimal de Kelly (continu) sur NDX / Composite.

Contexte : après l'échec cross-marché de l'overlay vol-targeting (Étape D
v2, `results/etape_D_v2_no_leverage.md`), exploration d'un angle DIFFÉRENT
— pas une tentative de prédire la direction, mais un choix normatif de
LEVIER optimal étant donné le rendement espéré et la volatilité prévue.

Formule de Kelly continue (Thorp) pour un actif unique :
    f* = μ_annualisé / σ²_annualisé
- μ_annualisé : rendement moyen historique en fenêtre EXPANSIVE (causal,
  aucune fuite — utilise uniquement r[:tr] à chaque ré-estimation).
- σ²_annualisé : variance walk-forward GJR-GARCH(1,1)-t déjà validée
  (Étape C, SPA p=0,0000), réutilisée telle quelle via
  `overlay.walk_forward_vol_forecast` (aucune réécriture du moteur).

Limite connue et assumée : μ (rendement espéré) est BEAUCOUP plus difficile
à estimer que σ² (c'est précisément pourquoi Étape B a échoué à prédire une
direction) — une moyenne expansive de rendements est un estimateur très
bruité, surtout en début d'échantillon. C'est pourquoi ce script teste
systématiquement le Kelly PLEIN (agressif, sensible au bruit d'estimation)
ET le demi-Kelly (pratique standard des professionnels, cf. Thorp 2006,
pour amortir cette incertitude d'estimation) — pas seulement le plein Kelly.

Plafond de levier CAP=3.0 fixé a priori (évite l'explosion pathologique de
f* quand σ² prévue est momentanément très faible en début de fenêtre),
jamais recalibré sur les résultats.

Ceci n'est PAS un test d'hypothèse avec critère de succès pré-enregistré
(comme B/C/D) — c'est une règle d'allocation NORMATIVE, évaluée
descriptivement (Sharpe/CAGR/MDD/Calmar vs Buy & Hold), pas sujette au
DSR (aucune sélection parmi plusieurs variantes concurrentes).
"""
import os
import sys
import warnings
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from overlay import walk_forward_vol_forecast  # noqa: E402
from prediction import backtest, trading_metrics  # noqa: E402

T0 = 750
REFIT_EVERY = 21
COST_BPS = 5.0
CAP = 3.0
ANNUALIZE_RET = 252.0

DATASETS = [
    ("Composite (5 ans)", "nasdaq_composite_daily.txt"),
    ("NDX (40 ans)", "nasdaq100_daily.txt"),
]


def kelly_fraction_path(r: np.ndarray, t0: int, refit_every: int) -> np.ndarray:
    """f*_t = mu_hat_annualise[:t] / vol_fcst_annualise[t]^2, causal (mu_hat
    et vol_fcst n'utilisent que r[:t], aucune fuite)."""
    fc = walk_forward_vol_forecast(r, t0, refit_every)  # reutilise le moteur GJR-t deja valide
    vol_fcst_frac = fc["vol_fcst"] / 100.0  # % -> fraction
    T = len(r)
    f_star = np.full(T, np.nan)
    for tr in range(t0, T, refit_every):
        mu_hat_ann = (r[:tr] / 100.0).mean() * ANNUALIZE_RET
        block = range(tr, min(tr + refit_every, T))
        for t in block:
            sigma2_ann = vol_fcst_frac[t] ** 2
            if sigma2_ann > 1e-12:
                f_star[t] = mu_hat_ann / sigma2_ann
    return f_star


def main():
    lines = [
        "# Analyse — Levier optimal de Kelly (continu) sur NDX / Composite",
        "",
        "f* = μ_annualisé (fenêtre expansive, causal) / σ²_annualisé "
        "(GJR-GARCH(1,1)-t walk-forward, Étape C, déjà validé). Plafond "
        f"CAP={CAP:.1f} fixé a priori. Kelly plein ET demi-Kelly testés "
        "(le plein Kelly est connu pour être très sensible au bruit "
        "d'estimation de μ — ceci n'est pas une découverte a posteriori, "
        "c'est pourquoi les deux variantes sont rapportées dès le départ).",
        "",
        "| Marché | Variante | Sharpe ann. | Calmar | MDD % | Rdt ann. % | "
        "Expo moy. | Expo max |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for label, fname in DATASETS:
        path = REPO_ROOT / "data" / fname
        df = load_ohlc(str(path))
        r = log_returns_pct(df).values
        r_bt = r / 100.0
        T = len(r)
        if T <= T0 + REFIT_EVERY:
            continue
        idx = np.arange(T0, T)

        f_star = kelly_fraction_path(r, T0, REFIT_EVERY)
        pos_full = np.clip(np.nan_to_num(f_star, nan=0.0), 0.0, CAP)
        pos_half = np.clip(np.nan_to_num(0.5 * f_star, nan=0.0), 0.0, CAP)
        pos_bh = np.ones(T)

        for name, pos in [("BuyHold", pos_bh), ("Kelly plein", pos_full), ("Demi-Kelly", pos_half)]:
            pnl = backtest(pos, r_bt, COST_BPS)[idx]
            me = trading_metrics(pnl)
            expo = pos[idx]
            lines.append(
                f"| {label} | {name} | {me['sharpe_ann']:+.2f} | {me['calmar']:+.2f} | "
                f"{me['max_drawdown_pct']:.1f} | {me['ann_return_pct']:+.1f} | "
                f"{expo.mean():.2f}× | {expo.max():.2f}× |"
            )

    lines.append("")
    lines.append(
        "**Lecture honnête** : contrairement au vol-targeting (Étape D), le levier de "
        "Kelly dépend directement de μ estimé — un estimateur bien plus bruité que la "
        "volatilité. Une exposition moyenne élevée ici reflète surtout la prime de "
        "risque actions historique moyenne sur la fenêtre, pas une compétence de "
        "timing. À interpréter comme un choix d'ALLOCATION (accepter plus de risque "
        "pour plus de rendement espéré), pas comme un signal prédictif."
    )

    out = ROOT / "results" / "analysis_kelly_criterion.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
