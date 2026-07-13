"""Etape D - Overlay defensif (vol-targeting sur GJR-GARCH(1,1)-t) vs Buy & Hold.
Produit results/etape_D_overlay.md.

Contexte (cf. CLAUDE.md) : Etape B - aucun signal directionnel ne bat Buy &
Hold net de couts et deflate. Etape C - GJR-GARCH(1,1)-t est le modele de
volatilite le plus robuste (SPA valide sur l'historique long). Ce script
teste si PILOTER L'EXPOSITION d'une position Buy & Hold via ces previsions de
volatilite (au lieu de predire une direction) reduit le max drawdown sans
sacrifier l'essentiel du rendement annualise.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping, cf. Etape C/D) :
- Univers de 3 variantes declarees, aucun ajout a posteriori (N=3 pour le DSR) :
    1. Buy & Hold pur                         - reference
    2. Overlay vol-targeting seul              - expo = clip(vol_cible/vol_prevue, 0, CAP)
    3. Overlay vol-targeting + coupe extreme   - + coupe totale si vol_prevue
       depasse le 95e percentile in-sample (regle a priori, cf. src/overlay.py)
- Vol-targeting : moteur GJR-GARCH(1,1)-t walk-forward (fenetre initiale 750
  obs, expansive, re-estimation tous les REFIT_EVERY j - meme cadence que
  l'Etape C ; 21 j sur l'historique long NDX pour rester praticable).
- Couts : 5 bps aller-retour, preleves sur le turnover de l'EXPOSITION (meme
  convention que backtest() de l'Etape B).
- Evaluation : Sharpe/Sortino/Calmar/MDD/rendement annualise NETS (Calmar et
  MDD en PRIORITE - c'est la metrique cible) + Deflated Sharpe Ratio (N=3).

CRITERE DE SUCCES EXPLICITE (a verifier, pas a supposer) : l'overlay n'est
utile que s'il reduit le MDD de facon MATERIELLE (>25% de reduction relative)
SANS perdre l'essentiel du rendement annualise de Buy & Hold (reste dans les
~80% du rendement annualise BuyHold). Verifie ci-dessous sur les deux jeux de
donnees ; si ce n'est pas le cas, le rapport le dit clairement plutot que de
presenter un resultat decevant comme un succes.
"""
import os
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct  # noqa: E402
from overlay import (  # noqa: E402
    EXTREME_CUT_FRAC,
    EXTREME_PCTL,
    build_overlay_positions,
)
from prediction import backtest, dsr, trading_metrics  # noqa: E402

# ------------------------------------------------------------------ protocole
T0 = 750
COST_BPS = 5.0
CAP = 1.5  # plafond de levier explicite (jamais de levier illimite)
MODELS = ["BuyHold", "VolTarget", "VolTarget+Cut"]

# re-estimation : cadence par jeu de donnees (defaut Etape C = 5j ; 21j sur
# l'historique long NDX, sinon des milliers de re-estimations GARCH - cf.
# CLAUDE.md). Surchargeable globalement par la variable d'env REFIT_EVERY.
DATASETS = [
    ("Composite (5 ans)", ROOT / "data" / "nasdaq_composite_daily.txt", 5),
    ("NDX (40 ans)", ROOT / "data" / "nasdaq100_daily.txt", 21),
]

OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "etape_D_overlay.md")

lines = []
w = lines.append
w("# Étape D — Overlay défensif (vol-targeting GJR-GARCH(1,1)-t) vs Buy & Hold\n")
w("Contexte : Étape B — aucun signal directionnel ne bat Buy & Hold net de "
  "coûts et déflaté. Étape C — GJR-GARCH(1,1)-t est le modèle de volatilité "
  "le plus robuste (SPA validé sur l'historique long). Ici on ne prédit "
  "aucune direction : on reste essentiellement investi (Buy & Hold) et on "
  "pilote l'EXPOSITION via la volatilité prévue.\n")
w(f"**Protocole figé** : fenêtre initiale {T0} obs, expansive ; coûts "
  f"{COST_BPS:.0f} bps aller-retour sur le turnover de l'exposition ; cap de "
  f"levier {CAP:.1f}× ; coupe extrême au {EXTREME_PCTL:.0f}e percentile "
  f"in-sample (fraction résiduelle {EXTREME_CUT_FRAC:.1f}) ; univers de "
  f"3 variantes (N={len(MODELS)} pour le DSR), figé avant évaluation.\n")

summary_rows = []  # pour le verdict final cross-dataset

for label, path, default_refit in DATASETS:
    refit_every = int(os.environ.get("REFIT_EVERY", default_refit))
    df = load_ohlc(str(path))
    r = log_returns_pct(df).values  # rendements log % (convention arch), pour le moteur GJR-t
    r_bt = r / 100.0  # rendements log NATURELS pour backtest()/trading_metrics (convention Etape B)
    dates = log_returns_pct(df).index
    T = len(r)
    if T <= T0 + refit_every:
        w(f"## {label}\n\n*Historique trop court pour T0={T0} — ignoré.*\n")
        continue

    # positions walk-forward : decidees avec l'info jusqu'a t-1, appliquees a r[t]
    # (meme convention causale que les previsions GJR-t de l'Etape C : aucun
    # lookahead, la variance de r[t] n'utilise que r[0..t-1]).
    pos = {"BuyHold": np.ones(T)}
    ov_vt = build_overlay_positions(r, T0, refit_every, CAP, with_extreme_cut=False)
    ov_cut = build_overlay_positions(r, T0, refit_every, CAP, with_extreme_cut=True)
    pos["VolTarget"] = ov_vt["pos"]
    pos["VolTarget+Cut"] = ov_cut["pos"]

    idx = np.arange(T0, T)
    pnl = {m: backtest(pos[m], r_bt, COST_BPS)[idx] for m in MODELS}
    metr = {m: trading_metrics(pnl[m]) for m in MODELS}

    sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
    var_trials = float(np.var(list(sr_daily.values()), ddof=1))
    T_oos = len(idx)
    dsr_out = {m: dsr(sr_daily[m], T_oos, var_trials, n_trials=len(MODELS),
                      skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])
              for m in MODELS}

    n_years = (dates[-1] - dates[T0]).days / 365.25
    w(f"## {label}\n")
    w(f"- OOS : {dates[T0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y} ({T_oos} obs, "
      f"~{n_years:.1f} ans), ré-estimation GJR-t tous les {refit_every} j.")
    expo = pos["VolTarget"][idx]
    expo_cut = pos["VolTarget+Cut"][idx]
    n_extreme = int((ov_cut["vol_fcst"][idx] > ov_cut["vol_thresh"][idx]).sum())
    w(f"- Exposition VolTarget : moy. {expo.mean():.2f}×, min {expo.min():.2f}×, "
      f"max {expo.max():.2f}× (cap {CAP:.1f}×).")
    w(f"- Coupe extrême déclenchée {n_extreme}/{T_oos} j "
      f"({100*n_extreme/T_oos:.1f}%) — exposition moy. VolTarget+Cut "
      f"{expo_cut.mean():.2f}×.\n")

    w("| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | "
      "Rdt ann. % | Profit factor | DSR |")
    w("|---|---|---|---|---|---|---|---|")
    for m in MODELS:
        me = metr[m]
        w(f"| {m} | {me['sharpe_ann']:+.2f} | {me['sortino_ann']:+.2f} | "
          f"{me['calmar']:+.2f} | {me['max_drawdown_pct']:.1f} | "
          f"{me['ann_return_pct']:+.1f} | {me['profit_factor']:.2f} | "
          f"{dsr_out[m]['dsr']:.3f} |")
    w("")

    bh = metr["BuyHold"]
    for m in ("VolTarget", "VolTarget+Cut"):
        me = metr[m]
        mdd_reduction = 1.0 - abs(me["max_drawdown_pct"]) / abs(bh["max_drawdown_pct"])
        ret_ratio = me["ann_return_pct"] / bh["ann_return_pct"] if bh["ann_return_pct"] != 0 else np.nan
        ok = mdd_reduction > 0.25 and ret_ratio >= 0.80
        summary_rows.append((label, m, mdd_reduction, ret_ratio, ok,
                             me["calmar"], bh["calmar"]))
        w(f"- **{m} vs BuyHold** : réduction MDD relative = "
          f"{100*mdd_reduction:+.1f}% (seuil >25%), rendement ann. conservé = "
          f"{100*ret_ratio:.1f}% du BuyHold (seuil ≥80%) → "
          + ("**critère de succès atteint**" if ok else "**critère de succès NON atteint**"))
    w("")

# ------------------------------------------------------------------- verdict
w("## Verdict — critère de succès explicite\n")
w("Succès = réduction du MDD >25% (relatif) **et** rendement annualisé "
  "conservé ≥80% de Buy & Hold. Vérifié, pas supposé :\n")
w("| Jeu de données | Variante | ΔMDD relatif | Rdt ann. / BuyHold | Calmar "
  "(overlay vs BH) | Critère |")
w("|---|---|---|---|---|---|")
any_success = False
for label, m, mdd_r, ret_r, ok, cal, cal_bh in summary_rows:
    any_success = any_success or ok
    w(f"| {label} | {m} | {100*mdd_r:+.1f}% | {100*ret_r:.1f}% | "
      f"{cal:+.2f} vs {cal_bh:+.2f} | {'OUI' if ok else 'NON'} |")
w("")
if any_success:
    w("**Verdict honnête** : le critère de succès est atteint pour au moins "
      "une combinaison jeu de données/variante ci-dessus (détail dans le "
      "tableau) — l'overlay apporte un bénéfice matériel de réduction du "
      "drawdown dans ce(s) cas, sans sacrifier l'essentiel du rendement. Il "
      "ne l'est PAS partout : ne pas généraliser au-delà de ce qui est "
      "montré dans le tableau.")
else:
    w("**Verdict honnête : le critère de succès N'EST ATTEINT nulle part.** "
      "Aucune variante d'overlay ne réduit le MDD de plus de 25% (relatif) "
      "tout en conservant ≥80% du rendement annualisé de Buy & Hold, sur "
      "aucun des deux jeux de données. L'overlay tel que construit "
      "(vol-targeting ± coupe extrême sur GJR-GARCH(1,1)-t) ne remplit pas "
      "l'objectif de l'Étape D — ce résultat est rapporté tel quel, sans le "
      "présenter comme un succès.")

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))
