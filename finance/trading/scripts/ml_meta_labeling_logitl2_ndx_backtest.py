"""ML-1 -- Meta-labeling sur le signal officiel Etape B (LogitL2), NDX.

Protocole et univers FIGES dans PREREG_ml_meta_labeling_logitl2_ndx.md,
committe AVANT tout calcul. Ce script n'ajoute aucune variante :
- primaire   : LogitL2 de l'Etape B, inchange (LogisticRegression C=0.5)
- secondaire : LogisticRegression C=0.5 sur build_features + primary_conf +
               primary_p_up, cible = "le pari primaire coincide-t-il avec le
               signe du label triple barrier ?"
- taille     : clip(2*(p_win-0.5), 0, 1), NaN -> 0 (filtre + sizing continu)
- position   : signe(p_up-0.5) * taille

Walk-forward T0=750, refit 21 j, purge/embargo 5 j (identique pour le
secondaire), couts 5 bps, triple barrier H=5 / +-1.5 sigma (ewm 20 j).
Fraction hors-marche remuneree a 0 % (Regle 10, declaree au PREREG).

Usage : python3 ml_meta_labeling_logitl2_ndx_backtest.py [donnees] [sortie_md]
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc  # noqa: E402
from meta_labeling import meta_labeled_position  # noqa: E402
from prediction import (  # noqa: E402
    backtest,
    build_features,
    dsr,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_signals,
)

# ---------------------------------------------------------------- protocole
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
SEED = 42
N_TRIALS_CUMUL = 405  # 400 brute-force ML 1-10 + 4 Etape B + 1 (ce cycle)

DATA = sys.argv[1] if len(sys.argv) > 1 else str(REPO_ROOT / "data" / "nasdaq100_daily.txt")
OUT = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "results" / "ml_meta_labeling_logitl2_ndx.md")
TAG = Path(OUT).stem


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def hgb():
    return HistGradientBoostingClassifier(
        max_depth=3, max_iter=150, learning_rate=0.05,
        l2_regularization=1.0, min_samples_leaf=40, random_state=SEED)


df = load_ohlc(DATA).set_index("date")
close = df["close"].astype(float)
logp = np.log(close)
r_fwd = (logp.shift(-1) - logp).values

X = build_features(df)
y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
y.index = df.index
n = len(df)
dates = df.index

# -------------------------------------------------- signaux (univers Etape B)
pos = {}
pos["BuyHold"] = np.ones(n)
mom = (logp - logp.shift(10)).values
pos["Momentum"] = np.where(np.isfinite(mom), np.sign(mom), 0.0)
pos["Momentum"][pos["Momentum"] == 0] = 1.0
pos["LogitL2"] = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), logistic,
                                      T0, REFIT_EVERY, EMBARGO, standardize=True)
pos["HistGB"] = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), hgb,
                                     T0, REFIT_EVERY, EMBARGO, standardize=False)

# ------------------------------------------------------ meta-labeling (ML-1)
meta = meta_labeled_position(X, y, logistic, logistic, T0, REFIT_EVERY, EMBARGO,
                             mode="continuous")
pos["Meta"] = meta["pos_final"]

# le primaire du pipeline meta doit etre STRICTEMENT le LogitL2 de l'Etape B :
# controle d'integrite (meme graine, meme walk-forward -> positions identiques)
assert np.allclose(meta["pos_primary"], pos["LogitL2"], equal_nan=True), \
    "primaire du meta-labeling != LogitL2 Etape B"

MODELS = ["BuyHold", "Momentum", "LogitL2", "HistGB", "Meta"]
oos = np.arange(T0, n - 1)

pnl = {m: backtest(pos[m], r_fwd, COST_BPS)[oos] for m in MODELS}
metr = {m: trading_metrics(pnl[m]) for m in MODELS}
turnover = {m: float(np.abs(np.diff(pos[m][oos], prepend=pos[m][oos][0])).mean())
            for m in MODELS}
exposure = {m: float(np.abs(pos[m][oos]).mean()) for m in MODELS}

# accuracy directionnelle (sur les jours ou la strategie parie reellement)
ylab = (y.values > 0).astype(float)
acc = {}
for m in ("Momentum", "LogitL2", "HistGB", "Meta"):
    p = pos[m][oos]
    valid = np.isfinite(p) & (p != 0) & np.isfinite(y.values[oos])
    acc[m] = float(((p[valid] > 0).astype(float) == ylab[oos][valid]).mean())

# break-even (bps/trade) au turnover observe
be = {}
for m in ("Momentum", "LogitL2", "HistGB", "Meta"):
    t_m = turnover[m]
    gross_mu = np.nanmean((pos[m] * r_fwd)[oos])
    be[m] = 1e4 * gross_mu / t_m if t_m > 0 else np.nan

# ------------------------------------------------------------------- DSR
sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
var_trials = float(np.var(list(sr_daily.values()), ddof=1))
T_oos = len(oos)
dsr_out = {m: dsr(sr_daily[m], T_oos, var_trials, n_trials=N_TRIALS_CUMUL,
                  skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])
           for m in MODELS}
# rappel : DSR a l'echelle de l'univers Etape B (N=4) pour comparer au rapport
# officiel etape_B_ndx100.md -- lecture secondaire, pas le verdict.
dsr_b = {m: dsr(sr_daily[m], T_oos, var_trials, n_trials=4,
                skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])
         for m in MODELS}

# --------------------------------------------------- critere de succes (PREREG)
bh, mt = metr["BuyHold"], metr["Meta"]
cond_a = (mt["sharpe_ann"] > bh["sharpe_ann"]) and (mt["ann_return_pct"] > bh["ann_return_pct"])
cond_b = np.isfinite(mt["calmar"]) and np.isfinite(bh["calmar"]) and (mt["calmar"] > bh["calmar"])
passed = bool(cond_a or cond_b)

np.savez(ROOT / "results" / f"{TAG}_pnl.npz",
         pos=pos["Meta"][oos], pos_primary=pos["LogitL2"][oos],
         r_asset=r_fwd[oos], dates=np.array(dates[oos].astype(str)),
         cost_bps=COST_BPS, var_trials=var_trials, n_trials=N_TRIALS_CUMUL)

# ----------------------------------------------------------------- rapport md
L = []
w = L.append
name = Path(DATA).stem
w(f"# ML-1 — Meta-labeling sur LogitL2 ({name})\n")
w(f"PREREG : `PREREG_ml_meta_labeling_logitl2_ndx.md` (committé avant calcul). "
  f"Script : `scripts/{Path(__file__).name}`.\n")

w("## 1. Mécanisme (figé au PREREG, n_trials local = 1)\n")
w("- **Primaire inchangé** : LogitL2 de l'Étape B (LogisticRegression C=0.5), "
  "features causales `build_features`, labels triple barrier H=5 / ±1,5σ (ewm 20 j).")
w("- **Secondaire** : LogisticRegression C=0.5 sur les mêmes features + "
  "`primary_conf`=|p_up−0,5|×2 + `primary_p_up`. Cible binaire : le pari primaire "
  "coïncide-t-il avec le signe du label triple barrier ?")
w("- **Position finale** = signe(p_up−0,5) × clip(2·(p_win−0,5), 0, 1) — filtre à "
  "seuil (p_win ≤ 0,5 → mise nulle) ET dimensionnement continu borné [0,1].")
w(f"- Walk-forward T0={T0}, refit {REFIT_EVERY} j, **purge/embargo {EMBARGO} j "
  "appliqué aussi au secondaire**, coûts "
  f"{COST_BPS:.0f} bps aller-retour sur |Δposition| (les Δ fractionnaires sont "
  "facturés au même tarif).")
w(f"- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au "
  "PREREG §4 (Règle 10), conservatrice pour l'hypothèse testée.")
w(f"- OOS = {T_oos} séances ({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}), "
  "fenêtre strictement identique à l'Étape B officielle.\n")

w("## 2. Avant / après meta-labeling (net de coûts)\n")
w("| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | "
  "Turnover moy./j | Exposition moy. |")
w("|---|---|---|---|---|---|---|---|---|")
for m in MODELS:
    x = metr[m]
    w(f"| {m} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | {x['calmar']:+.2f} | "
      f"{x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % | "
      f"{x['profit_factor']:.2f} | {turnover[m]:.3f} | {exposure[m]:.2f} |")
w("")
w("*`Meta` = LogitL2 filtré/dimensionné par le méta-modèle. `LogitL2` = le même "
  "signal primaire nu (référence avant meta-labeling).*\n")

w("## 3. Accuracy directionnelle et coût de rupture\n")
w("| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |")
w("|---|---|---|")
for m in ("Momentum", "LogitL2", "HistGB", "Meta"):
    w(f"| {m} | {100*acc[m]:.2f} % | {be[m]:+.2f} |")
w("")

w("## 4. Deflated Sharpe Ratio\n")
w(f"σ²(SR quotidiens des {len(MODELS)} signaux) = {var_trials:.4e}. Deux lectures :\n")
w(f"| Signal | Sharpe quot. | DSR (n_trials={N_TRIALS_CUMUL}, campagne ML entière) | "
  "DSR (n_trials=4, échelle Étape B) |")
w("|---|---|---|---|")
for m in MODELS:
    w(f"| {m} | {sr_daily[m]:+.4f} | **{dsr_out[m]['dsr']:.3f}** | {dsr_b[m]['dsr']:.3f} |")
w("")
w(f"*La colonne de gauche est celle qui compte : n_trials={N_TRIALS_CUMUL} = 400 "
  "(brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ce cycle). "
  "Jamais réduit à 1 (Règle 2). La colonne de droite n'est là que pour comparer "
  "aux chiffres publiés de `etape_B_ndx100.md`.*\n")

w("## 5. Verdict (critère chiffré du PREREG §5)\n")
w(f"- **(A)** Sharpe Meta ({mt['sharpe_ann']:+.2f}) > Sharpe BuyHold "
  f"({bh['sharpe_ann']:+.2f}) **ET** rendement Meta ({mt['ann_return_pct']:+.1f} %) > "
  f"rendement BuyHold ({bh['ann_return_pct']:+.1f} %) → "
  f"**{'satisfait' if cond_a else 'NON satisfait'}**.")
w(f"- **(B)** Calmar Meta ({mt['calmar']:+.2f}) > Calmar BuyHold "
  f"({bh['calmar']:+.2f}) → **{'satisfait' if cond_b else 'NON satisfait'}**.")
w("")
w(f"### {'PASS niveau 1' if passed else 'FAIL'}\n")
d_sharpe = mt["sharpe_ann"] - metr["LogitL2"]["sharpe_ann"]
d_turn = turnover["Meta"] - turnover["LogitL2"]
w(f"Effet du meta-labeling sur le signal primaire : Sharpe {metr['LogitL2']['sharpe_ann']:+.2f} "
  f"→ {mt['sharpe_ann']:+.2f} ({d_sharpe:+.2f}), turnover {turnover['LogitL2']:.3f} "
  f"→ {turnover['Meta']:.3f} ({d_turn:+.3f}/j), MDD "
  f"{metr['LogitL2']['max_drawdown_pct']:.1f} % → {mt['max_drawdown_pct']:.1f} %, "
  f"exposition moyenne {exposure['LogitL2']:.2f} → {exposure['Meta']:.2f}.")
if passed:
    w("\nCe PASS est un **niveau 1 uniquement**. Il n'a de valeur qu'après la "
      "batterie de validation renforcée (§2.4 du backlog ML, 5 contrôles a-e) — "
      "voir `ml_meta_labeling_logitl2_ndx_battery.md`. Aucune notification n'est "
      "émise sur un PASS niveau 1 seul.")
else:
    w("\nLe critère pré-enregistré n'est pas atteint : le meta-labeling **ne suffit "
      "pas** à faire passer LogitL2 au-dessus de Buy & Hold. La batterie de "
      "validation renforcée n'est pas déclenchée (elle ne s'applique qu'à un PASS "
      "niveau 1). Résultat rapporté tel quel, sans ajustement du mécanisme ni du "
      "critère a posteriori (Règle 1).")
w("")

w("## 6. Notes de traçabilité (Règle 6)\n")
w(f"- **Baseline recalculée, pas recopiée.** Le LogitL2 mesuré ici "
  f"({metr['LogitL2']['sharpe_ann']:+.2f} de Sharpe) diffère du chiffre publié dans "
  "`results/etape_B_ndx100.md` (+0,30) : `triple_barrier_labels` a été modifié depuis "
  "(σ locale = écart-type glissant strict sur [t−20, t) au lieu d'un ewm expansif ; "
  "les deux versions sont causales, mais les labels diffèrent, cf. "
  "`results/etape_B_phase1_fixed.md`). Les 5 lignes du tableau §2 proviennent **du "
  "même run, du même code et des mêmes labels** : la comparaison avant/après est donc "
  "interne et cohérente, ce qui est ce dont dépend le verdict.")
w("- **Sharpe invariant d'échelle.** L'exposition moyenne du candidat "
  f"({exposure['Meta']:.2f}) est faible, mais appliquer un levier uniforme ne "
  "changerait ni le Sharpe (invariant d'échelle, hors coûts) ni le Calmar (rendement "
  "et drawdown se multiplient par le même facteur) : le verdict du §5 ne dépend pas "
  "du niveau de levier retenu. Aucune variante avec levier n'a donc été évaluée "
  "(cela aurait ajouté un essai sans changer la conclusion).")
w(f"- **σ²(SR essais)** utilisée par les deux colonnes DSR du §4 est calculée sur les "
  f"{len(MODELS)} signaux de ce run (BuyHold, Momentum, LogitL2, HistGB, Meta) ; la "
  "colonne « échelle Étape B » n'est donc pas strictement identique au tableau publié "
  "(qui l'estimait sur 4 signaux) — elle sert d'ordre de grandeur, pas de verdict.")
w("- Fichier de positions sauvegardé pour audit : "
  f"`results/{TAG}_pnl.npz` (positions OOS, rendements, dates, coût, σ², n_trials).")
w("")

Path(OUT).write_text("\n".join(L))
print("\n".join(L))
print(f"\n[VERDICT] {'PASS_NIVEAU_1' if passed else 'FAIL'} | {TAG}")
