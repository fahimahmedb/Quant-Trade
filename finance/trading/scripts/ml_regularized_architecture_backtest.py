"""ML-3 -- Architecture unique bien regularisee : gradient boosting avec early
stopping sur folds PURGES (protocole officiel de l'Etape B, NDX).

Protocole et univers FIGES dans PREREG_ml_regularized_architecture.md, committe
AVANT tout calcul (commit 5fa9761). Ce script n'ajoute aucune variante :

- candidat  : HistGradientBoostingClassifier, hyperparametres identiques a ceux
              du HistGB de l'Etape B (max_depth=3, learning_rate=0.05,
              l2_regularization=1.0, min_samples_leaf=40, random_state=42),
              SEUL max_iter change de statut : plafond 400 au lieu de 150 fixe,
              la valeur effective k* etant choisie par early stopping purge.
- early stop: decoupe CHRONOLOGIQUE (jamais aleatoire) de la fenetre
              d'entrainement -- validation = 20 % les plus recents, purge
              interne de 5 lignes (= H) juste avant, apprentissage = le reste.
              k* = argmin de la log-loss de validation sur les stades de
              boosting (staged_predict_proba), contraint a [10, 400].
              Modele deploye = re-ajustement sur la fenetre d'entrainement
              COMPLETE a max_iter=k*. Aucune donnee de test n'intervient.
- features  : build_features(df) seul (exog=None) -- aucune feature exogene
              (enseignement ML-2, PREREG §4).
- position  : signe(p_up-0.5) dans {-1,+1}, 0 pendant le warmup. AUCUN sizing
              probabiliste (enseignement ML-1, PREREG §5).
- PAS de GridSearchCV / RandomizedSearchCV : un seul jeu d'hyperparametres fixe
  a priori, une seule definition de candidat. n_trials local = 1.

Walk-forward T0=750, refit 21 j, purge/embargo 5 j, couts 5 bps, triple barrier
H=5 / +-1.5 sigma. Fraction hors-marche remuneree a 0 % (Regle 10, PREREG §8).

Usage : python3 ml_regularized_architecture_backtest.py [donnees] [sortie_md]
"""
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc  # noqa: E402
from prediction import (  # noqa: E402
    backtest,
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
N_TRIALS_CUMUL = 407  # 400 brute-force ML 1-10 + 4 Etape B + ML-1 + ML-2 + ML-3

# ------------------------------------------- architecture ML-3 (PREREG §3.1)
GB_PARAMS = dict(max_depth=3, learning_rate=0.05, l2_regularization=1.0,
                 min_samples_leaf=40, random_state=SEED, early_stopping=False)
MAX_ITER = 400        # plafond de capacite (PREREG §3.1)
K_MIN = 10            # borne basse de k* (PREREG §3.2)
VAL_FRACTION = 0.20   # bloc de validation = 20 % les plus RECENTS
PURGE_GAP = H         # purge interne entre apprentissage et validation
MIN_TRAIN_ROWS = 300  # garde-fou degenere (PREREG §3.2 point 4)
FALLBACK_ITER = 150   # capacite de repli = valeur Etape B

DATA = sys.argv[1] if len(sys.argv) > 1 else str(REPO_ROOT / "data" / "nasdaq100_daily.txt")
OUT = (sys.argv[2] if len(sys.argv) > 2
       else str(ROOT / "results" / "ml_regularized_architecture.md"))
TAG = Path(OUT).stem


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def hgb_fixed():
    """HistGB de l'Etape B : capacite FIXE 150, aucune selection."""
    return HistGradientBoostingClassifier(max_iter=FALLBACK_ITER, **GB_PARAMS)


class PurgedEarlyStoppingHGB:
    """Gradient boosting a capacite choisie par early stopping purge.

    Interface sklearn minimale (fit / predict_proba) attendue par
    `walk_forward_proba`. Les lignes recues sont deja purgees de l'embargo
    walk-forward et rangees en ordre CHRONOLOGIQUE strict : la decoupe interne
    est donc simplement positionnelle.

    Journalise `k_` (capacite retenue) et `mode_` ("early_stopping" ou
    "fallback") pour les diagnostics du rapport.
    """

    def __init__(self):
        self.k_ = None
        self.mode_ = None
        self.val_loss_ = None
        self.model_ = None

    def _fallback(self, X, y):
        self.k_, self.mode_ = FALLBACK_ITER, "fallback"
        self.model_ = HistGradientBoostingClassifier(
            max_iter=FALLBACK_ITER, **GB_PARAMS).fit(X, y)
        return self

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y).astype(int)
        m = len(X)
        if m < MIN_TRAIN_ROWS:
            return self._fallback(X, y)

        n_val = int(VAL_FRACTION * m)
        val_start = m - n_val
        fit_end = val_start - PURGE_GAP            # purge interne de H lignes
        Xa, ya = X[:fit_end], y[:fit_end]          # apprentissage (le passe)
        Xv, yv = X[val_start:], y[val_start:]      # validation (le plus recent)
        if (fit_end < MIN_TRAIN_ROWS or len(np.unique(ya)) < 2
                or len(np.unique(yv)) < 2):
            return self._fallback(X, y)

        probe = HistGradientBoostingClassifier(max_iter=MAX_ITER, **GB_PARAMS)
        probe.fit(Xa, ya)
        best_k, best_loss = K_MIN, np.inf
        for k, p in enumerate(probe.staged_predict_proba(Xv), start=1):
            if k < K_MIN:
                continue
            loss = log_loss(yv, p, labels=[0, 1])
            if loss < best_loss:
                best_loss, best_k = loss, k
        self.k_, self.mode_, self.val_loss_ = int(best_k), "early_stopping", float(best_loss)
        # modele deploye : re-ajustement sur la fenetre d'entrainement COMPLETE
        # (apprentissage + purge + validation) a la capacite selectionnee.
        self.model_ = HistGradientBoostingClassifier(max_iter=self.k_, **GB_PARAMS).fit(X, y)
        return self

    def predict_proba(self, X):
        return self.model_.predict_proba(X)


FITTED = []  # journal des modeles candidats (diagnostics k*)


def hgb_es():
    est = PurgedEarlyStoppingHGB()
    FITTED.append(est)
    return est


def signals_from_proba(p):
    """signe(p_up - 0.5), 0 quand aucun modele n'est entraine (identique a
    walk_forward_signals) -- explicite ici pour garder p_up pour les diagnostics."""
    return np.where(np.isfinite(p), np.where(p > 0.5, 1.0, -1.0), 0.0)


df = load_ohlc(DATA).set_index("date")
close = df["close"].astype(float)
logp = np.log(close)
r_fwd = (logp.shift(-1) - logp).values

X = build_features(df)  # univers endogene de l'Etape B, exog=None (PREREG §4)
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

t_start = time.time()
p_logit = walk_forward_proba(X, y, logistic, T0, REFIT_EVERY, EMBARGO, standardize=True)
pos["LogitL2"] = signals_from_proba(p_logit)
print(f"[{time.time()-t_start:6.1f}s] LogitL2 ok", file=sys.stderr)

p_hgb = walk_forward_proba(X, y, hgb_fixed, T0, REFIT_EVERY, EMBARGO, standardize=False)
pos["HistGB"] = signals_from_proba(p_hgb)
print(f"[{time.time()-t_start:6.1f}s] HistGB (capacite fixe 150) ok", file=sys.stderr)

# ------------------------------------------------------- candidat ML-3
p_es = walk_forward_proba(X, y, hgb_es, T0, REFIT_EVERY, EMBARGO, standardize=False)
pos["HistGB-ES"] = signals_from_proba(p_es)
print(f"[{time.time()-t_start:6.1f}s] HistGB-ES (candidat) ok", file=sys.stderr)

MODELS = ["BuyHold", "Momentum", "LogitL2", "HistGB", "HistGB-ES"]
CAND = "HistGB-ES"
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

# ------------------------------- diagnostics de capacite k* (PREREG §5)
ks = np.array([e.k_ for e in FITTED if e.k_ is not None], dtype=float)
n_fallback = sum(1 for e in FITTED if e.mode_ == "fallback")
k_at_cap = int((ks >= MAX_ITER).sum()) if len(ks) else 0

# --------------------------------------------- controle a-plat (PREREG §4)
flat_share = float((pos[CAND][oos] == 0).mean())
first_bet = int(np.argmax(pos[CAND][oos] != 0)) if (pos[CAND][oos] != 0).any() else -1
warmup_only = bool(flat_share > 0 and (pos[CAND][oos][first_bet:] != 0).all()) or flat_share == 0

# --------------------------------------------------- critere de succes (PREREG §7)
bh, cd = metr["BuyHold"], metr[CAND]
cond_a = (cd["sharpe_ann"] > bh["sharpe_ann"]) and (cd["ann_return_pct"] > bh["ann_return_pct"])
cond_b = (np.isfinite(cd["calmar"]) and np.isfinite(bh["calmar"])
          and cd["calmar"] > bh["calmar"])
passed = bool(cond_a or cond_b)

np.savez(ROOT / "results" / f"{TAG}_pnl.npz",
         pos=pos[CAND][oos], pos_primary=pos["HistGB"][oos],
         r_asset=r_fwd[oos], dates=np.array(dates[oos].astype(str)),
         cost_bps=COST_BPS, var_trials=var_trials, n_trials=N_TRIALS_CUMUL,
         k_star=ks)

# ----------------------------------------------------------------- rapport md
L = []
w = L.append
name = Path(DATA).stem
w(f"# ML-3 — Architecture unique bien régularisée : gradient boosting à early stopping purgé ({name})\n")
w("PREREG : `PREREG_ml_regularized_architecture.md` (committé avant calcul, "
  f"commit `5fa9761`). Script : `scripts/{Path(__file__).name}`.\n")

w("## 1. Architecture (figée au PREREG, n_trials local = 1)\n")
w("- **Un seul modèle non linéaire**, choisi et justifié au PREREG §2 **avant "
  "tout calcul** : gradient boosting (`HistGradientBoostingClassifier`) avec "
  "early stopping sur folds purgés. La variante MLP du backlog a été écartée "
  "explicitement (pas de `torch` dans l'environnement, pas de dropout dans "
  "`sklearn`, et un MLP changerait simultanément trop de choses par rapport à "
  "la baseline) ; elle n'est **pas** repoussée à un sous-cycle de repli.")
w(f"- **Hyperparamètres identiques à ceux du `HistGB` de l'Étape B** "
  f"(`max_depth=3`, `learning_rate=0,05`, `l2_regularization=1,0`, "
  f"`min_samples_leaf=40`, `random_state={SEED}`) — repris tels quels, donc "
  "aucun essai caché. **Seul `max_iter` change de statut** : plafond "
  f"{MAX_ITER} au lieu d'une valeur fixe de {FALLBACK_ITER}.")
w("- **Early stopping purgé** : à chaque ré-estimation, la fenêtre "
  "d'entraînement (déjà purgée de l'embargo walk-forward) est coupée "
  f"chronologiquement — validation = les **{100*VAL_FRACTION:.0f} % les plus "
  f"récents**, purge interne de **{PURGE_GAP} lignes** (= H) juste avant, "
  "apprentissage = le reste. `k*` = itération minimisant la log-loss de "
  f"validation (`staged_predict_proba`), contrainte à [{K_MIN}, {MAX_ITER}]. "
  "Le modèle déployé est ré-ajusté sur la fenêtre d'entraînement **complète** "
  "à `max_iter=k*`. La découpe aléatoire par défaut de scikit-learn "
  "(`early_stopping=True`) est **refusée** : elle mélangerait des labels "
  "triple-barrière chevauchants entre apprentissage et validation.")
w("- **Aucun grid-search** : ni `GridSearchCV` ni `RandomizedSearchCV`, aucun "
  "hyperparamètre choisi sur une métrique de trading. La seule quantité "
  "sélectionnée (`k*`) l'est sur une log-loss **interne à la fenêtre "
  "d'entraînement**, jamais sur l'OOS.")
w(f"- **Features** : les {len(X.columns)} colonnes endogènes de "
  "`build_features(df)`, `exog=None` — **aucune feature exogène** "
  "(enseignement ML-2 : une feature à historique court met le modèle à plat et "
  "ampute son rendement ; ce cycle porte sur l'architecture seule).")
w("- **Position** : `signe(p_up − 0,5)` ∈ {−1, +1}, 0 tant qu'aucun modèle "
  "n'est entraîné. **Aucun sizing probabiliste** (enseignement ML-1, déclaré "
  "au PREREG §5) : aucune calibration n'est en jeu, l'effet mesuré est celui "
  "de l'architecture seule.")
w(f"- Walk-forward T0={T0}, refit {REFIT_EVERY} j, purge/embargo {EMBARGO} j, "
  f"coûts {COST_BPS:.0f} bps aller-retour sur |Δposition| — **protocole de "
  "l'Étape B officielle, non modifié**.")
w("- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au "
  "PREREG §8 (Règle 10). Le candidat est ±1 hors warmup.")
w(f"- OOS = {T_oos} séances ({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}), "
  "fenêtre strictement identique à l'Étape B officielle, à ML-1 et à ML-2.\n")

w("## 2. Performance out-of-sample (nette de coûts, fenêtre OOS complète)\n")
w("| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | "
  "Turnover moy./j | Exposition moy. |")
w("|---|---|---|---|---|---|---|---|---|")
for m in MODELS:
    x = metr[m]
    w(f"| {m} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | {x['calmar']:+.2f} | "
      f"{x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % | "
      f"{x['profit_factor']:.2f} | {turnover[m]:.3f} | {exposure[m]:.2f} |")
w("")
w("*`HistGB-ES` = le candidat (capacité choisie par early stopping purgé). "
  "`HistGB` = la MÊME architecture à capacité fixe 150, recalculée dans CE run "
  "(même code, mêmes labels, même graine) : c'est la comparaison interne qui "
  "isole l'effet de la régularisation de capacité, et rien d'autre.*\n")

w("## 3. Accuracy directionnelle et coût de rupture\n")
w("| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |")
w("|---|---|---|")
for m in ("Momentum", "LogitL2", "HistGB", CAND):
    w(f"| {m} | {100*acc[m]:.2f} % | {be[m]:+.2f} |")
w("")

w("## 4. Capacité sélectionnée par l'early stopping (diagnostic, PREREG §5)\n")
if len(ks):
    w(f"- Ré-estimations du candidat : **{len(FITTED)}** (dont {n_fallback} en "
      f"mode de repli `max_iter={FALLBACK_ITER}`).")
    w(f"- `k*` retenu : min **{int(ks.min())}**, médiane **{int(np.median(ks))}**, "
      f"moyenne **{ks.mean():.0f}**, max **{int(ks.max())}**.")
    w(f"- Blocs atteignant le plafond {MAX_ITER} : **{k_at_cap}** "
      f"({100*k_at_cap/len(ks):.1f} %) — le plafond n'est donc "
      f"{'pas' if k_at_cap / len(ks) < 0.10 else 'PAS'} la contrainte active "
      "dans la grande majorité des cas"
      + ("." if k_at_cap / len(ks) < 0.10 else
         " ; à surveiller, une part élevée indiquerait que la borne de calcul "
         "bride la sélection."))
    w(f"- Part des blocs où `k*` < {FALLBACK_ITER} (capacité **inférieure** à "
      f"celle de l'Étape B) : **{100*float((ks < FALLBACK_ITER).mean()):.1f} %**.")
else:
    w("- Aucune ré-estimation journalisée (anomalie).")
w("")

w("## 5. Deflated Sharpe Ratio\n")
w(f"σ²(SR quotidiens des {len(MODELS)} signaux) = {var_trials:.4e}. Deux lectures :\n")
w(f"| Signal | Sharpe quot. | DSR (n_trials={N_TRIALS_CUMUL}, campagne ML entière) | "
  "DSR (n_trials=4, échelle Étape B) |")
w("|---|---|---|---|")
for m in MODELS:
    w(f"| {m} | {sr_daily[m]:+.4f} | **{dsr_out[m]['dsr']:.3f}** | {dsr_b[m]['dsr']:.3f} |")
w("")
w(f"*La colonne de gauche est celle qui compte : n_trials={N_TRIALS_CUMUL} = 400 "
  "(brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1) + 1 "
  "(ML-2) + 1 (ce cycle). Jamais réduit à 1 (Règle 2). La colonne de droite ne "
  "sert qu'à comparer aux chiffres publiés de `etape_B_ndx100.md`.*\n")

w("## 6. Contrôle « à plat » exigé au PREREG §4\n")
w(f"- Part des séances OOS où le candidat est à plat (position 0) : "
  f"**{100*flat_share:.2f} %**.")
w(f"- Ces séances sont-elles exclusivement le warmup initial du walk-forward "
  f"(bloc contigu en tête d'OOS, aucune interruption ensuite) : "
  f"**{'oui' if warmup_only else 'NON — anomalie à investiguer'}**.")
w("- Attendu : le candidat n'utilise que des features endogènes disponibles sur "
  "toute la période ; toute autre valeur signalerait un bug (le contrôle est "
  "pré-enregistré précisément pour ne pas reproduire l'artefact de ML-2).\n")

w("## 7. Verdict (critère chiffré du PREREG §7)\n")
w(f"- **(A)** Sharpe {CAND} ({cd['sharpe_ann']:+.2f}) > Sharpe BuyHold "
  f"({bh['sharpe_ann']:+.2f}) **ET** rendement {CAND} ({cd['ann_return_pct']:+.1f} %) > "
  f"rendement BuyHold ({bh['ann_return_pct']:+.1f} %) → "
  f"**{'satisfait' if cond_a else 'NON satisfait'}**.")
w(f"- **(B)** Calmar {CAND} ({cd['calmar']:+.2f}) > Calmar BuyHold "
  f"({bh['calmar']:+.2f}) → **{'satisfait' if cond_b else 'NON satisfait'}**.")
w("")
w(f"### {'PASS niveau 1' if passed else 'FAIL'}\n")
d_sharpe = cd["sharpe_ann"] - metr["HistGB"]["sharpe_ann"]
d_acc = 100 * (acc[CAND] - acc["HistGB"])
w(f"Effet de la régularisation de capacité (early stopping purgé) sur la MÊME "
  f"architecture : Sharpe {metr['HistGB']['sharpe_ann']:+.2f} → "
  f"{cd['sharpe_ann']:+.2f} ({d_sharpe:+.2f}), accuracy "
  f"{100*acc['HistGB']:.2f} % → {100*acc[CAND]:.2f} % ({d_acc:+.2f} pt), "
  f"rendement annualisé {metr['HistGB']['ann_return_pct']:+.1f} % → "
  f"{cd['ann_return_pct']:+.1f} %, MDD {metr['HistGB']['max_drawdown_pct']:.1f} % "
  f"→ {cd['max_drawdown_pct']:.1f} %, turnover {turnover['HistGB']:.3f} → "
  f"{turnover[CAND]:.3f}/j, break-even {be['HistGB']:+.2f} → {be[CAND]:+.2f} "
  "bps/trade.")
if passed:
    w("\nCe PASS est un **niveau 1 uniquement**. Il n'a de valeur qu'après la "
      "batterie de validation renforcée (§2.4 du backlog ML, 5 contrôles a-e) — "
      f"voir `{TAG}_battery.md`. Aucune notification n'est émise sur un PASS "
      "niveau 1 seul.")
else:
    w("\nLe critère pré-enregistré n'est pas atteint : régulariser la capacité "
      "d'une architecture non linéaire par early stopping purgé **ne suffit "
      "pas** à la faire passer au-dessus de Buy & Hold. La batterie de "
      "validation renforcée n'est pas déclenchée (elle ne s'applique qu'à un "
      "PASS niveau 1). Résultat rapporté tel quel, sans changement "
      "d'architecture, d'hyperparamètres, de sizing ni de critère a posteriori "
      "(Règle 1) — en particulier **aucun basculement vers la variante MLP**, "
      "explicitement interdit par le PREREG §11.")
w("")

w("## 8. Notes de traçabilité (Règle 6)\n")
w("- **Baseline recalculée, pas recopiée.** Le `HistGB` mesuré ici "
  f"({metr['HistGB']['sharpe_ann']:+.2f} de Sharpe) peut différer du chiffre "
  "publié dans `results/etape_B_ndx100.md` (+0,23) : `triple_barrier_labels` a "
  "été modifié depuis (σ locale = écart-type glissant strict sur [t−20, t)). "
  "Les 5 lignes du §2 proviennent **du même run, du même code et des mêmes "
  "labels** — la comparaison avec/sans early stopping est donc interne et "
  "cohérente, et c'est d'elle que dépend le verdict.")
w("- **Absence de fuite par la validation** : la découpe est positionnelle sur "
  "des lignes déjà rangées chronologiquement, la validation est le bloc le plus "
  "RÉCENT, et un purge de "
  f"{PURGE_GAP} lignes (= H) sépare apprentissage et validation, ce qui retire "
  "les événements dont la triple barrière chevauche le bloc de validation. "
  "Aucune ligne postérieure à `tr − embargo` n'entre dans un `fit` "
  "(garanti par `walk_forward_proba`, `finance/src/prediction.py`).")
w("- **`k*` est sélectionné sur une log-loss, jamais sur une métrique de "
  "trading** : aucun retour d'information de l'OOS vers la capacité du modèle.")
w(f"- **Erratum de rédaction (sans effet sur le calcul)** : le PREREG §4 écrit "
  f"« les 21 colonnes endogènes » ; `build_features(df)` en produit en réalité "
  f"**{len(X.columns)}**. Le chiffre 21 était repris tel quel du PREREG ML-2, "
  "qui contenait déjà cette coquille. Aucune conséquence : le script consomme "
  "`build_features(df)` **en bloc**, sans sélection ni comptage de colonnes — "
  "l'univers de features est donc bien celui de l'Étape B officielle, "
  "inchangé. Signalé ici plutôt que corrigé dans le PREREG, qui ne doit pas "
  "être modifié après calcul (Règle 1).")
w(f"- **σ²(SR essais)** des deux colonnes DSR du §5 est calculée sur les "
  f"{len(MODELS)} signaux de ce run ; la colonne « échelle Étape B » sert "
  "d'ordre de grandeur, pas de verdict.")
w("- Fichier de positions sauvegardé pour audit : "
  f"`results/{TAG}_pnl.npz` (positions OOS, positions de la baseline HistGB, "
  "rendements, dates, coût, σ², n_trials, série des `k*`).")
w("")

Path(OUT).write_text("\n".join(L))
print("\n".join(L))
print(f"\n[VERDICT] {'PASS_NIVEAU_1' if passed else 'FAIL'} | {TAG}")
