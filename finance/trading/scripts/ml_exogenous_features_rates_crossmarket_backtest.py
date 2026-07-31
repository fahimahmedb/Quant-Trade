"""ML-2 -- Features exogenes taux / cross-marche ajoutees au LogitL2 (Etape B).

Protocole et univers FIGES dans
PREREG_ml_exogenous_features_rates_crossmarket.md, committe AVANT tout calcul.
Ce script n'ajoute aucune variante :
- modele    : LogitL2 de l'Etape B, inchange (LogisticRegression C=0.5)
- features  : build_features(df) + EXACTEMENT 5 colonnes exogenes
              (DGS10 niveau, pente DGS10-DGS3MO, variations quotidiennes
               10y et 3mo, rendement DAX decale d'une seance)
- alignement: derniere observation STRICTEMENT anterieure a t (aucun ffill
              d'observation future, aucune utilisation du jour t lui-meme)
- position  : signe(p_up-0.5) dans {-1,+1}, 0 pendant le warmup.
              AUCUN sizing probabiliste (enseignement ML-1, declare au PREREG).

Walk-forward T0=750, refit 21 j, purge/embargo 5 j, couts 5 bps, triple barrier
H=5 / +-1.5 sigma. Fraction hors-marche remuneree a 0 % (Regle 10, PREREG §7).

Usage : python3 ml_exogenous_features_rates_crossmarket_backtest.py [donnees] [sortie_md]
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
from prediction import (  # noqa: E402
    backtest,
    build_exogenous_features,
    build_features,
    dsr,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_proba,
)

# ---------------------------------------------------------------- protocole
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
SEED = 42
N_TRIALS_CUMUL = 406  # 400 brute-force ML 1-10 + 4 Etape B + 1 (ML-1) + 1 (ML-2)

DGS10 = str(REPO_ROOT / "data" / "dgs10_daily.csv")
DGS3MO = str(REPO_ROOT / "data" / "dgs3mo_daily.csv")
DAX = str(REPO_ROOT / "data" / "dax_daily.txt")

DATA = sys.argv[1] if len(sys.argv) > 1 else str(REPO_ROOT / "data" / "nasdaq100_daily.txt")
OUT = (sys.argv[2] if len(sys.argv) > 2
       else str(ROOT / "results" / "ml_exogenous_features_rates_crossmarket.md"))
TAG = Path(OUT).stem


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def hgb():
    return HistGradientBoostingClassifier(
        max_depth=3, max_iter=150, learning_rate=0.05,
        l2_regularization=1.0, min_samples_leaf=40, random_state=SEED)


def signals_from_proba(p):
    """signe(p_up - 0.5), 0 quand aucun modele n'est entraine (identique a
    walk_forward_signals) -- explicite ici pour garder p_up pour les diagnostics."""
    return np.where(np.isfinite(p), np.where(p > 0.5, 1.0, -1.0), 0.0)


df = load_ohlc(DATA).set_index("date")
close = df["close"].astype(float)
logp = np.log(close)
r_fwd = (logp.shift(-1) - logp).values

EXOG = build_exogenous_features(df.index, DGS10, DGS3MO, DAX)
X = build_features(df)                 # univers endogene de l'Etape B (inchange)
X_exog = build_features(df, exog=EXOG)  # + 5 colonnes exogenes (candidat ML-2)
assert list(X_exog.columns[:len(X.columns)]) == list(X.columns)
assert X_exog[X.columns].equals(X), "build_features(exog=...) altere les features endogenes"

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

p_logit = walk_forward_proba(X, y, logistic, T0, REFIT_EVERY, EMBARGO, standardize=True)
pos["LogitL2"] = signals_from_proba(p_logit)
p_hgb = walk_forward_proba(X, y, hgb, T0, REFIT_EVERY, EMBARGO, standardize=False)
pos["HistGB"] = signals_from_proba(p_hgb)

# ------------------------------------------------------- candidat ML-2
p_exog = walk_forward_proba(X_exog, y, logistic, T0, REFIT_EVERY, EMBARGO, standardize=True)
pos["LogitL2Exog"] = signals_from_proba(p_exog)

MODELS = ["BuyHold", "Momentum", "LogitL2", "HistGB", "LogitL2Exog"]
CAND = "LogitL2Exog"
oos = np.arange(T0, n - 1)

pnl_full = {m: backtest(pos[m], r_fwd, COST_BPS) for m in MODELS}
pnl = {m: pnl_full[m][oos] for m in MODELS}
metr = {m: trading_metrics(pnl[m]) for m in MODELS}
turnover = {m: float(np.abs(np.diff(pos[m][oos], prepend=pos[m][oos][0])).mean())
            for m in MODELS}
exposure = {m: float(np.abs(pos[m][oos]).mean()) for m in MODELS}

# accuracy directionnelle (jours ou la strategie parie reellement)
ylab = (y.values > 0).astype(float)
acc = {}
for m in ("Momentum", "LogitL2", "HistGB", CAND):
    p = pos[m][oos]
    valid = np.isfinite(p) & (p != 0) & np.isfinite(y.values[oos])
    acc[m] = float(((p[valid] > 0).astype(float) == ylab[oos][valid]).mean())

# break-even (bps/trade) au turnover observe
be = {}
for m in ("Momentum", "LogitL2", "HistGB", CAND):
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
dsr_b = {m: dsr(sr_daily[m], T_oos, var_trials, n_trials=4,
                skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])
         for m in MODELS}

# --------------------------------------------------- critere de succes (PREREG §6)
bh, cd = metr["BuyHold"], metr[CAND]
cond_a = (cd["sharpe_ann"] > bh["sharpe_ann"]) and (cd["ann_return_pct"] > bh["ann_return_pct"])
cond_b = (np.isfinite(cd["calmar"]) and np.isfinite(bh["calmar"])
          and cd["calmar"] > bh["calmar"])
passed = bool(cond_a or cond_b)

# ------------------- lecture secondaire : fenetre restreinte (PREREG §5)
active = oos[np.isfinite(p_exog[oos])]
# lecture secondaire pertinente uniquement si la fenetre operationnelle est un
# sous-ensemble STRICT de l'OOS (sinon elle est identique et n'apprend rien)
has_restricted = len(active) > 250 and int(active[0]) > int(oos[0])
if has_restricted:
    r0 = int(active[0])
    restr = np.arange(r0, n - 1)
    metr_r = {m: trading_metrics(pnl_full[m][restr]) for m in (CAND, "LogitL2", "BuyHold")}
    cond_a_r = (metr_r[CAND]["sharpe_ann"] > metr_r["BuyHold"]["sharpe_ann"]
                and metr_r[CAND]["ann_return_pct"] > metr_r["BuyHold"]["ann_return_pct"])
    cond_b_r = metr_r[CAND]["calmar"] > metr_r["BuyHold"]["calmar"]

# ------------------- controle anti-artefact obligatoire (PREREG §5)
flat_share = float((pos[CAND][oos] == 0).mean())
dot0, dot1 = pd.Timestamp("2000-01-01"), pd.Timestamp("2002-12-31")
dmask = np.asarray((dates[oos] >= dot0) & (dates[oos] <= dot1))
dot = {}
if int(dmask.sum()) > 20:
    for m in (CAND, "BuyHold"):
        dot[m] = trading_metrics(pnl[m][dmask])
    dot_flat = float((pos[CAND][oos][dmask] == 0).mean())

np.savez(ROOT / "results" / f"{TAG}_pnl.npz",
         pos=pos[CAND][oos], pos_primary=pos["LogitL2"][oos],
         r_asset=r_fwd[oos], dates=np.array(dates[oos].astype(str)),
         cost_bps=COST_BPS, var_trials=var_trials, n_trials=N_TRIALS_CUMUL)

# ----------------------------------------------------------------- rapport md
L = []
w = L.append
name = Path(DATA).stem
w(f"# ML-2 — Features exogènes taux / cross-marché sur LogitL2 ({name})\n")
w("PREREG : `PREREG_ml_exogenous_features_rates_crossmarket.md` (committé avant "
  f"calcul). Script : `scripts/{Path(__file__).name}`.\n")

w("## 1. Mécanisme (figé au PREREG, n_trials local = 1)\n")
w("- **Modèle inchangé** : LogitL2 de l'Étape B (`LogisticRegression(C=0.5, "
  "max_iter=1000)`), standardisation calée sur la fenêtre d'entraînement, labels "
  "triple barrier H=5 / ±1,5σ.")
w(f"- **Features** : les {len(X.columns)} colonnes endogènes de `build_features` "
  f"+ **{len(EXOG.columns)} colonnes exogènes** — `exog_dgs10_level`, "
  "`exog_slope_10y_3mo` (DGS10−DGS3MO), `exog_dgs10_chg`, `exog_dgs3mo_chg`, "
  "`exog_dax_ret_lag1`.")
w("- **Alignement causal** : chaque feature exogène au jour `t` vaut la (les) "
  "dernière(s) observation(s) **strictement antérieure(s)** à `t` de sa série "
  "(`obs_date < t`), calendrier propre à chaque série, aucun `ffill` "
  "d'observation future. Motif documenté aux cycles non-ML #110/#140 : le DAX "
  "clôture ~17:30 CET, soit **pendant** la séance NDX du même jour — utiliser sa "
  "clôture du jour `t` serait une fuite.")
w("- **Position** : `signe(p_up − 0,5)` ∈ {−1, +1}, 0 tant qu'aucun modèle n'est "
  "entraîné. **Aucun sizing probabiliste** (enseignement ML-1, déclaré au "
  "PREREG §3 avant tout calcul) : aucune calibration n'est donc en jeu.")
w(f"- Walk-forward T0={T0}, refit {REFIT_EVERY} j, purge/embargo {EMBARGO} j, "
  f"coûts {COST_BPS:.0f} bps aller-retour sur |Δposition| — **protocole de "
  "l'Étape B officielle, non modifié**.")
w("- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au "
  "PREREG §7 (Règle 10), conservatrice pour l'hypothèse testée.")
w(f"- OOS = {T_oos} séances ({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}), "
  "fenêtre strictement identique à l'Étape B officielle et à ML-1.\n")

w("## 2. Avec / sans features exogènes (net de coûts, fenêtre OOS complète)\n")
w("| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | "
  "Turnover moy./j | Exposition moy. |")
w("|---|---|---|---|---|---|---|---|---|")
for m in MODELS:
    x = metr[m]
    w(f"| {m} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | {x['calmar']:+.2f} | "
      f"{x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % | "
      f"{x['profit_factor']:.2f} | {turnover[m]:.3f} | {exposure[m]:.2f} |")
w("")
w("*`LogitL2Exog` = le candidat (endogène + exogène). `LogitL2` = le même modèle "
  "avec les seules features endogènes, recalculé dans CE run (même code, mêmes "
  "labels) : c'est la comparaison interne qui isole l'effet des features "
  "exogènes.*\n")

w("## 3. Accuracy directionnelle et coût de rupture\n")
w("| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |")
w("|---|---|---|")
for m in ("Momentum", "LogitL2", "HistGB", CAND):
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
  "(brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ce "
  "cycle). Jamais réduit à 1 (Règle 2). La colonne de droite ne sert qu'à "
  "comparer aux chiffres publiés de `etape_B_ndx100.md`.*\n")

w("## 5. Disponibilité des données exogènes — contrôle anti-artefact (PREREG §5)\n")
w(f"- Le DAX ne commence qu'au 01/11/1999 : le candidat est **à plat (position 0) "
  f"sur {100*flat_share:.1f} % des séances OOS**, dont toute la période "
  "antérieure à sa première estimation.")
if dot:
    w(f"- Fenêtre dot-com (01/2000 → 12/2002, {int(dmask.sum())} séances) : MDD "
      f"candidat {dot[CAND]['max_drawdown_pct']:.1f} % vs Buy & Hold "
      f"{dot['BuyHold']['max_drawdown_pct']:.1f} % ; le candidat y est à plat sur "
      f"{100*dot_flat:.1f} % des séances.")
else:
    w("- Fenêtre dot-com non couverte par cet échantillon.")
w("- Cette pénalité (rendement annualisé mécaniquement réduit par les séances à "
  "plat) est **assumée et pré-enregistrée** : la fenêtre de verdict reste celle "
  "de l'Étape B, sans raccourci, comme au cycle ML-1.\n")

if not has_restricted:
    w("Sur cet échantillon, les séries exogènes couvrent **toute** la fenêtre "
      "OOS : la « fenêtre restreinte » du PREREG §5 coïncide avec la fenêtre de "
      "verdict, il n'y a donc aucune lecture secondaire distincte à rapporter.\n")

if has_restricted:
    w("### 5.1 Lecture secondaire — fenêtre restreinte (aucun effet sur le verdict)\n")
    w(f"Fenêtre où le candidat est réellement opérationnel : "
      f"{dates[r0]:%d/%m/%Y} → {dates[n-2]:%d/%m/%Y} ({len(restr)} séances), "
      "**Buy & Hold recalculé sur exactement la même fenêtre**.\n")
    w("| Signal | Sharpe ann. | Calmar | Rdt ann. | MDD |")
    w("|---|---|---|---|---|")
    for m in ("BuyHold", "LogitL2", CAND):
        x = metr_r[m]
        w(f"| {m} | {x['sharpe_ann']:+.2f} | {x['calmar']:+.2f} | "
          f"{x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % |")
    w("")
    w(f"Sur cette fenêtre : critère (A) {'satisfait' if cond_a_r else 'NON satisfait'}, "
      f"critère (B) {'satisfait' if cond_b_r else 'NON satisfait'}. "
      "**Lecture informative uniquement** — le verdict du §6 reste celui de la "
      "fenêtre OOS complète (PREREG §5).\n")
    d_bh = metr_r["BuyHold"]["sharpe_ann"] - metr["BuyHold"]["sharpe_ann"]
    sens = ("affaiblit" if d_bh < 0 else "renforce")
    biais = ("favorise" if d_bh < 0 else "défavorise")
    ctx = (" — elle s'ouvre à quelques mois du sommet de marché de 2000, donc "
           "juste avant le krach dot-com" if dates[r0].year <= 2001 else "")
    w("**Avertissement de lecture (obligatoire, quel que soit le sens du "
      f"résultat)** : cette fenêtre écarte les {r0 - int(oos[0])} premières "
      f"séances OOS ({dates[oos[0]]:%d/%m/%Y} → {dates[r0-1]:%d/%m/%Y}){ctx}. "
      f"Elle ne change pas seulement le candidat : elle {sens} aussi le "
      f"benchmark — Sharpe Buy & Hold {metr['BuyHold']['sharpe_ann']:+.2f} "
      f"(fenêtre complète) → {metr_r['BuyHold']['sharpe_ann']:+.2f} (fenêtre "
      f"restreinte, {d_bh:+.2f}). Un raccourcissement de fenêtre qui déplace "
      f"ainsi le benchmark {biais} mécaniquement le candidat, indépendamment de "
      "sa qualité prédictive. La fenêtre est **imposée par la disponibilité du "
      "DAX (01/11/1999), pas choisie** — mais c'est exactement pour ce type de "
      "biais que le PREREG §5 lui refuse tout effet sur le verdict. Un candidat "
      "qui ne franchit le seuil que sur cette fenêtre n'est PAS un PASS et ne "
      "déclenche NI la batterie renforcée NI de notification.\n")

w("## 6. Verdict (critère chiffré du PREREG §6)\n")
w(f"- **(A)** Sharpe {CAND} ({cd['sharpe_ann']:+.2f}) > Sharpe BuyHold "
  f"({bh['sharpe_ann']:+.2f}) **ET** rendement {CAND} ({cd['ann_return_pct']:+.1f} %) > "
  f"rendement BuyHold ({bh['ann_return_pct']:+.1f} %) → "
  f"**{'satisfait' if cond_a else 'NON satisfait'}**.")
w(f"- **(B)** Calmar {CAND} ({cd['calmar']:+.2f}) > Calmar BuyHold "
  f"({bh['calmar']:+.2f}) → **{'satisfait' if cond_b else 'NON satisfait'}**.")
w("")
w(f"### {'PASS niveau 1' if passed else 'FAIL'}\n")
d_sharpe = cd["sharpe_ann"] - metr["LogitL2"]["sharpe_ann"]
d_acc = 100 * (acc[CAND] - acc["LogitL2"])
w(f"Effet des features exogènes sur le modèle : Sharpe {metr['LogitL2']['sharpe_ann']:+.2f} "
  f"→ {cd['sharpe_ann']:+.2f} ({d_sharpe:+.2f}), accuracy {100*acc['LogitL2']:.2f} % → "
  f"{100*acc[CAND]:.2f} % ({d_acc:+.2f} pt), rendement annualisé "
  f"{metr['LogitL2']['ann_return_pct']:+.1f} % → {cd['ann_return_pct']:+.1f} %, MDD "
  f"{metr['LogitL2']['max_drawdown_pct']:.1f} % → {cd['max_drawdown_pct']:.1f} %, "
  f"exposition moyenne {exposure['LogitL2']:.2f} → {exposure[CAND]:.2f}.")
if passed:
    if cond_b and not cond_a:
        w("\n**Critère atteint par la seule branche (B) Calmar** : l'examen "
          "anti-artefact du §5 est donc obligatoire (PREREG §5) — une part du "
          "gain de Calmar peut venir du fait que le candidat est à plat pendant "
          "le krach dot-com faute de données exogènes, pas d'un edge. Les "
          "contrôles b et c de la batterie renforcée tranchent.")
    w("\nCe PASS est un **niveau 1 uniquement**. Il n'a de valeur qu'après la "
      "batterie de validation renforcée (§2.4 du backlog ML, 5 contrôles a-e) — "
      f"voir `{TAG}_battery.md`. Aucune notification n'est émise sur un PASS "
      "niveau 1 seul.")
else:
    w("\nLe critère pré-enregistré n'est pas atteint : l'ajout de features "
      "exogènes taux/cross-marché **ne suffit pas** à faire passer LogitL2 "
      "au-dessus de Buy & Hold. La batterie de validation renforcée n'est pas "
      "déclenchée (elle ne s'applique qu'à un PASS niveau 1). Résultat rapporté "
      "tel quel, sans ajustement des features, du sizing ni du critère a "
      "posteriori (Règle 1).")
w("")

w("## 7. Notes de traçabilité (Règle 6)\n")
w("- **Baseline recalculée, pas recopiée.** Le `LogitL2` mesuré ici "
  f"({metr['LogitL2']['sharpe_ann']:+.2f} de Sharpe) diffère du chiffre publié "
  "dans `results/etape_B_ndx100.md` (+0,30) : `triple_barrier_labels` a été "
  "modifié depuis (σ locale = écart-type glissant strict sur [t−20, t)). Les "
  "5 lignes du §2 proviennent **du même run, du même code et des mêmes "
  "labels** — la comparaison avec/sans exogènes est donc interne et cohérente, "
  "et c'est d'elle que dépend le verdict.")
w("- **Non-régression vérifiée par assertion dans le script** : "
  "`build_features(df, exog=...)` reproduit à l'identique les colonnes "
  "endogènes de `build_features(df)` (assert en tête de script) — aucun script "
  "existant (Étapes B/C/D, ML-1) n'est affecté par l'extension.")
w("- **Causalité vérifiée par construction** : `_asof_prev` "
  "(`finance/src/prediction.py`) utilise `np.searchsorted(..., side=\"left\") − 1`, "
  "soit strictement `obs_date < t`. Une observation du jour `t` ne peut pas "
  "entrer dans une feature du jour `t`.")
w(f"- **σ²(SR essais)** des deux colonnes DSR du §4 est calculée sur les "
  f"{len(MODELS)} signaux de ce run ; la colonne « échelle Étape B » sert "
  "d'ordre de grandeur, pas de verdict.")
w("- Fichier de positions sauvegardé pour audit : "
  f"`results/{TAG}_pnl.npz` (positions OOS, rendements, dates, coût, σ², n_trials).")
w("")

Path(OUT).write_text("\n".join(L))
print("\n".join(L))
print(f"\n[VERDICT] {'PASS_NIVEAU_1' if passed else 'FAIL'} | {TAG}")
