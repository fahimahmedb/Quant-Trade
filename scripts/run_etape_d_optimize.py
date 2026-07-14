"""Etape D (optimisation) - Grid-search fige des parametres de l'overlay
vol-targeting (GJR-GARCH(1,1)-t) sur NDX (historique long).
Produit results/etape_D_overlay_optimized.md.

Contexte (cf. CLAUDE.md, resultats etablis A/B/C, reutilises tels quels) :
Etape C - GJR-GARCH(1,1)-t est le modele de volatilite le plus robuste (SPA
valide sur NDX, p=0.0000 a h=1). Etape D (premiere passe, resultats/
etape_D_overlay.md, CAP=1.5 / percentile de coupe=95 fixes a priori) : sur
NDX, VolTarget+Cut reduit deja le MDD (-63.3% vs -82.9% BuyHold, soit -23.7%
relatif) tout en AUGMENTANT le rendement annualise (+16.4% vs +14.5%), mais
la reduction de MDD reste sous le seuil de succes (>25% relatif). Cette
passe optimise les DEUX parametres explicites de l'overlay (cap d'exposition
et percentile de coupe extreme) par grid-search FIGE, pour verifier si un
reglage different atteint le critere de succes - sans jamais toucher au
moteur GARCH ni au protocole walk-forward.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping) :
- Univers de 12 combinaisons EXACTEMENT (2 parametres x grille fixee AVANT
  evaluation, aucun ajout a posteriori, N=12 pour le DSR) :
    vol_target_cap        in {1.00, 1.25, 1.50, 2.00}   (plafond de levier)
    extreme_cut_percentile in {90, 95, 99}                (seuil de coupe,
                                                            percentile IN-SAMPLE
                                                            de la vol GJR-t
                                                            prevue, fenetre
                                                            d'entrainement
                                                            uniquement)
  La coupe elle-meme reste la regle a priori deja fixee en Etape D (coupe
  TOTALE, EXTREME_CUT_FRAC=0.0, cf. src/overlay.py) - seul le PERCENTILE de
  declenchement varie ici, jamais la fraction residuelle.
- Un seul dataset : NDX (data/nasdaq100_daily.txt, 40 ans, plusieurs cycles,
  krach 2000-2002 inclus - le cas d'usage vise par l'overlay).
- Walk-forward T0=750, expansive, re-estimation GJR-t tous les REFIT_EVERY j
  (21 par defaut sur l'historique long, meme cadence que l'Etape C/D).
- Couts : 5 bps aller-retour sur le turnover de l'EXPOSITION (backtest() de
  src/prediction.py, meme convention que le reste du repo).
- Optimisation cout : le moteur GJR-t ne depend NI du cap NI du percentile de
  coupe -> un seul passage walk-forward (walk_forward_vol_forecast_multi)
  calcule les previsions et les 3 seuils de percentile en une fois ; les 12
  combinaisons ne font que reappliquer clip/coupe (vectorise), aucun refit
  redondant.
- Evaluation : Sharpe/Sortino/Calmar/MDD (PRIORITE)/rendement annualise/
  turnover NETS de couts + Deflated Sharpe Ratio (N=12, famille des 12
  combos ; Buy & Hold sert de reference hors-famille, DSR non calcule pour
  elle ici - deja etabli en Etape B/D).

CRITERE DE SUCCES (identique a l'Etape D, verifie pas suppose) : reduction du
MDD >25% relatif vs Buy & Hold ET rendement annualise conserve >=80% de Buy &
Hold.
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
    extreme_cut,
    vol_target_exposure,
    walk_forward_vol_forecast_multi,
)
from prediction import backtest, dsr, trading_metrics  # noqa: E402

# ------------------------------------------------------------------ protocole
T0 = 750
COST_BPS = 5.0
CAP_GRID = [1.00, 1.25, 1.50, 2.00]          # fige AVANT evaluation
PCTL_GRID = [90, 95, 99]                      # fige AVANT evaluation
DATA_PATH = ROOT / "data" / "nasdaq100_daily.txt"
DEFAULT_REFIT = 21
REFIT_EVERY = int(os.environ.get("REFIT_EVERY", DEFAULT_REFIT))
OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "etape_D_overlay_optimized.md")

df = load_ohlc(str(DATA_PATH))
r = log_returns_pct(df).values          # rendements log % (convention arch/GJR-t)
r_bt = r / 100.0                        # rendements log naturels (convention backtest/trading_metrics)
dates = log_returns_pct(df).index
T = len(r)
assert T > T0 + REFIT_EVERY, "historique NDX trop court pour T0/REFIT_EVERY"

idx = np.arange(T0, T)
T_oos = len(idx)
n_years = (dates[-1] - dates[T0]).days / 365.25

# --------------------------------------------------------- reference Buy & Hold
pos_bh = np.ones(T)
pnl_bh = backtest(pos_bh, r_bt, COST_BPS)[idx]
metr_bh = trading_metrics(pnl_bh)

# -------------------------------------------------- previsions (un seul passage)
# Le moteur GJR-t (fit_arch/garch_path) ne depend ni du cap ni du percentile de
# coupe -> calcule une fois pour les 3 percentiles de la grille (cf. docstring).
fc = walk_forward_vol_forecast_multi(r, T0, REFIT_EVERY, PCTL_GRID)
vol_fcst, vol_target, vol_thresh = fc["vol_fcst"], fc["vol_target"], fc["vol_thresh"]

# ------------------------------------------------------------------ grid-search
rows = []  # (cap, pctl, metrics_dict, turnover, sharpe_daily)
for cap in CAP_GRID:
    expo_vt = vol_target_exposure(vol_fcst, vol_target, cap)
    for pctl in PCTL_GRID:
        expo = extreme_cut(expo_vt, vol_fcst, vol_thresh[pctl], EXTREME_CUT_FRAC)
        pos = np.nan_to_num(expo, nan=0.0)
        pnl = backtest(pos, r_bt, COST_BPS)[idx]
        me = trading_metrics(pnl)
        turnover = float(np.mean(np.abs(np.diff(pos[idx], prepend=pos[idx][0]))))
        rows.append({"cap": cap, "pctl": pctl, "metrics": me, "turnover": turnover,
                     "pos": pos})

# ----------------------------------------------------------------- DSR (N=12)
sr_daily = [row["metrics"]["sharpe_daily"] for row in rows]
var_trials = float(np.var(sr_daily, ddof=1))
n_trials = len(rows)
for row in rows:
    me = row["metrics"]
    row["dsr"] = dsr(me["sharpe_daily"], T_oos, var_trials, n_trials,
                     skew=me["skew"], kurt_excess=me["excess_kurt"])["dsr"]

# ------------------------------------------------------------- criteres/succes
for row in rows:
    me = row["metrics"]
    mdd_reduction = 1.0 - abs(me["max_drawdown_pct"]) / abs(metr_bh["max_drawdown_pct"])
    ret_ratio = (me["ann_return_pct"] / metr_bh["ann_return_pct"]
                if metr_bh["ann_return_pct"] != 0 else np.nan)
    row["mdd_reduction"] = mdd_reduction
    row["ret_ratio"] = ret_ratio
    row["ok"] = bool(mdd_reduction > 0.25 and ret_ratio >= 0.80)

# tri par MDD (priorite absolue) : du drawdown le moins severe au plus severe
rows_sorted = sorted(rows, key=lambda x: x["metrics"]["max_drawdown_pct"], reverse=True)

any_success = any(row["ok"] for row in rows)
# Tri : critere de succes atteint d'abord, puis reduction de MDD (arrondie -
# les ex-aequo a +/-0.1pp sont du bruit numerique, pas un signal), puis Calmar
# (metrique cible secondaire explicitement demandee) comme depart-age.
best = max(rows, key=lambda x: (x["ok"], round(x["mdd_reduction"], 3), x["metrics"]["calmar"]))

# ------------------------------------------------------------------------ rapport
lines = []
w = lines.append
w("# Étape D (optimisation) — Grid-search vol-targeting × coupe extrême (NDX)\n")
w("Contexte : Étape D (première passe, `results/etape_D_overlay.md`) a testé "
  "un seul réglage a priori (cap 1.5×, coupe au 95e percentile) : réduction "
  "MDD de +23.7% relatif sur NDX, sous le seuil de succès (>25%). Ce "
  "grid-search explore les **deux paramètres explicites** de l'overlay "
  "(cap d'exposition, percentile de coupe extrême) sur une grille **figée "
  "avant évaluation**, sans toucher au moteur GJR-GARCH(1,1)-t ni à la "
  "règle de coupe elle-même (coupe totale, `EXTREME_CUT_FRAC="
  f"{EXTREME_CUT_FRAC:.1f}`, inchangée).\n")
w(f"**Protocole figé** : NDX (`{DATA_PATH.name}`), fenêtre initiale {T0} obs "
  f"expansive, ré-estimation GJR-t tous les {REFIT_EVERY} j, coûts "
  f"{COST_BPS:.0f} bps aller-retour sur le turnover de l'exposition. "
  f"OOS : {dates[T0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y} ({T_oos} obs, "
  f"~{n_years:.1f} ans). Grille : `vol_target_cap` ∈ {CAP_GRID} × "
  f"`extreme_cut_percentile` ∈ {PCTL_GRID} = **{n_trials} combinaisons "
  "exactement**, aucun ajout a posteriori (N=12 pour le DSR).\n")
w(f"**Référence Buy & Hold** : Sharpe ann. {metr_bh['sharpe_ann']:+.2f}, "
  f"Calmar {metr_bh['calmar']:+.2f}, MDD {metr_bh['max_drawdown_pct']:.1f}%, "
  f"rendement ann. {metr_bh['ann_return_pct']:+.1f}%.\n")

w("## Grille des 12 combinaisons (triée par MDD, priorité absolue)\n")
w("| cap | pctl coupe | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | "
  "Rdt ann. % | Turnover | DSR (N=12) | ΔMDD rel. | Rdt/BH | Critère |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for row in rows_sorted:
    me = row["metrics"]
    w(f"| {row['cap']:.2f}× | {row['pctl']:.0f}e | {me['sharpe_ann']:+.2f} | "
      f"{me['sortino_ann']:+.2f} | {me['calmar']:+.2f} | "
      f"{me['max_drawdown_pct']:.1f} | {me['ann_return_pct']:+.1f} | "
      f"{row['turnover']:.3f} | {row['dsr']:.3f} | "
      f"{100*row['mdd_reduction']:+.1f}% | {100*row['ret_ratio']:.1f}% | "
      f"{'OUI' if row['ok'] else 'non'} |")
w("")
w(f"| BuyHold (référence) | — | {metr_bh['sharpe_ann']:+.2f} | "
  f"{metr_bh['sortino_ann']:+.2f} | {metr_bh['calmar']:+.2f} | "
  f"{metr_bh['max_drawdown_pct']:.1f} | {metr_bh['ann_return_pct']:+.1f} | "
  "0.000 | — | — | 100.0% | — |")
w("")

w("## Verdict — meilleure combinaison et critère de succès\n")
w("Succès = réduction du MDD >25% (relatif) **et** rendement annualisé "
  "conservé ≥80% de Buy & Hold. Vérifié, pas supposé, sur les 12 "
  "combinaisons de la grille figée ci-dessus.\n")
w(f"**Meilleure combinaison** (critère de succès atteint en priorité, puis "
  f"réduction de MDD, puis Calmar comme départage entre ex-aequo) : cap "
  f"**{best['cap']:.2f}×**, coupe au "
  f"**{best['pctl']:.0f}e percentile** — ΔMDD relatif "
  f"{100*best['mdd_reduction']:+.1f}%, rendement conservé "
  f"{100*best['ret_ratio']:.1f}% du Buy & Hold, Calmar {best['metrics']['calmar']:+.2f} "
  f"(vs {metr_bh['calmar']:+.2f} Buy & Hold), MDD {best['metrics']['max_drawdown_pct']:.1f}% "
  f"(vs {metr_bh['max_drawdown_pct']:.1f}% Buy & Hold).\n")

if any_success:
    n_ok = sum(1 for row in rows if row["ok"])
    w(f"**Verdict honnête** : {n_ok}/12 combinaison(s) de la grille atteignent "
      "le critère de succès explicite (>25% réduction MDD, ≥80% rendement "
      "conservé) sur NDX. Le réglage optimal ci-dessus apporte un bénéfice "
      "matériel de réduction du drawdown sans sacrifier l'essentiel du "
      "rendement Buy & Hold. Rappel anti-data-snooping : ce résultat provient "
      "d'une grille fixée a priori (12 combinaisons, DSR déflaté sur cette "
      "famille), pas d'un balayage libre a posteriori — mais il reste "
      "spécifique à ce jeu de données (NDX) et n'a pas été re-vérifié sur le "
      "Composite (5 ans) dans cette passe.")
else:
    w("**Verdict honnête : aucune des 12 combinaisons de la grille n'atteint "
      "le critère de succès complet** (>25% réduction MDD relatif ET ≥80% "
      "du rendement annualisé Buy & Hold conservé) sur NDX. La meilleure "
      "combinaison ci-dessus s'en rapproche mais ne le remplit pas "
      "intégralement — ce résultat est rapporté tel quel, sans le présenter "
      "comme un succès. Optimiser le cap et le percentile de coupe améliore "
      "marginalement le compromis MDD/rendement par rapport au réglage a "
      "priori (1.5× / 95e, cf. `etape_D_overlay.md`), mais ne change pas la "
      "conclusion qualitative de l'Étape D.")

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))
