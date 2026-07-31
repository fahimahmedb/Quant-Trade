"""ML-4 -- Cross-market pooling : entrainement CONJOINT sur 3 marches
genetiquement independants (Russell 2000, S&P 500, DAX), evaluation
walk-forward SEPAREE par marche.

Protocole et univers FIGES dans PREREG_ml_crossmarket_pooling.md, committe
AVANT tout calcul (commit 064ae48). Ce script n'ajoute aucune variante :

- candidat  : LogitL2Pooled = LogisticRegression(C=0.5, max_iter=1000)
              -- hyperparametres du LogitL2 de l'Etape B a l'identique.
              SEULE difference avec la baseline : la composition de
              l'echantillon d'ENTRAINEMENT (3 marches pooles).
- pooling   : purge en DATE DE FIN DE LABEL (PREREG §3.4) --
              ligne i du marche k retenue ssi L_k[i] = date_k[min(i+H, n_k-1)]
              est STRICTEMENT anterieure a la date de debut du bloc de test
              du marche evalue. Equivalence exacte avec le masque de
              walk_forward_proba quand k == m (prouvee au PREREG, verifiee
              numeriquement ici par le test de non-regression).
- standard. : par marche, sur les lignes d'entrainement de CE marche
              (PREREG §3.5). Les lignes de test du marche m utilisent
              (mu_m, sd_m) -- statistiques d'entrainement de leur propre marche.
- features  : build_features(df) seul (exog=None). Aucune feature exogene ni
              cross-marche (enseignement ML-2).
- position  : signe(p_up-0.5) dans {-1,+1}, 0 pendant le warmup. AUCUN sizing
              probabiliste (enseignement ML-1).
- accuracy / turnover / break-even : DIAGNOSTICS uniquement, jamais un critere
              (enseignement ML-3).

Walk-forward T0=750, refit 21 j, purge/embargo 5 j (forme calendaire), couts
5 bps, triple barrier H=5 / +-1.5 sigma. n_trials cumule = 408.

Usage : python3 ml_crossmarket_pooling_backtest.py [sortie_md]
"""
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, quality_report  # noqa: E402
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
MIN_ROWS_BLOCK = 100      # garde-fou identique a walk_forward_proba (PREREG §3.4-4)
N_TRIALS_CUMUL = 408      # 400 brute-force + 4 Etape B + ML-1 + ML-2 + ML-3 + ML-4

# ------------------------------------------------ univers de marches (FIGE)
MARKETS = [
    ("Russell 2000", REPO_ROOT / "data" / "russell2000_daily.txt", "russell2000"),
    ("S&P 500", REPO_ROOT / "data" / "sp500_daily.txt", "sp500"),
    ("DAX", REPO_ROOT / "data" / "dax_daily.txt", "dax"),
]

OUT = (sys.argv[1] if len(sys.argv) > 1
       else str(ROOT / "results" / "ml_crossmarket_pooling.md"))

CAND = "LogitL2Pooled"
SOLO = "LogitL2Solo"
MODELS = ["BuyHold", "Momentum", SOLO, CAND]


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def signals_from_proba(p):
    """signe(p_up - 0.5), 0 quand aucun modele n'est entraine."""
    return np.where(np.isfinite(p), np.where(p > 0.5, 1.0, -1.0), 0.0)


# ============================================================ 1. chargement
print("== chargement + quality_report (Regle 7) ==", file=sys.stderr)
M = {}
QREP = {}
for name, path, tag in MARKETS:
    df = load_ohlc(str(path))
    QREP[name] = quality_report(df)          # leve si dates dupliquees / OHLC incoherent
    df = df.set_index("date")
    logp = np.log(df["close"].astype(float))
    X = build_features(df)                    # exog=None (PREREG §3.2)
    y = triple_barrier_labels(df.reset_index(), horizon=H,
                              vol_span=VOL_SPAN, mult=BARRIER_MULT)
    y.index = df.index
    n = len(df)
    dates = df.index.values.astype("datetime64[ns]")
    # date de fin de label (barriere verticale au plus tard), PREREG §3.4-2
    idx_end = np.minimum(np.arange(n) + H, n - 1)
    label_end = dates[idx_end]
    Xv = X.values.astype(float)
    yv = y.values.astype(float)
    usable = np.isfinite(yv) & np.all(np.isfinite(Xv), axis=1)
    M[name] = dict(tag=tag, path=str(path), df=df, X=X, Xv=Xv, y=y, yv=yv, n=n,
                   dates=dates, dates_idx=df.index, label_end=label_end,
                   usable=usable, logp=logp,
                   r_fwd=(logp.shift(-1) - logp).values)
    print(f"   {name:<13} n={n:>6}  {df.index[0]:%d/%m/%Y} -> {df.index[-1]:%d/%m/%Y}"
          f"  usable={int(usable.sum())}", file=sys.stderr)

FEATURE_NAMES = list(M[MARKETS[0][0]]["X"].columns)
for name, _, _ in MARKETS:      # coherence de l'univers de features entre marches
    assert list(M[name]["X"].columns) == FEATURE_NAMES, "features heterogenes entre marches"


# =================================================== 2. walk-forward poole
def pooled_walk_forward(m_name, pool_names, log=None):
    """p_up OOS du marche `m_name`, modele entraine sur le pool `pool_names`.

    Purge en date de fin de label (PREREG §3.4), standardisation par marche
    (PREREG §3.5). `log` (optionnel) recoit un dict de diagnostics par refit.
    """
    mm = M[m_name]
    Xm, n = mm["Xv"], mm["n"]
    dates_m = mm["dates"]
    proba = np.full(n, np.nan)
    for tr in range(T0, n, REFIT_EVERY):
        d_test = dates_m[tr]                       # debut du bloc de test
        blocks_X, blocks_y, sizes = [], [], {}
        mu_m = sd_m = None
        for k in pool_names:
            mk = M[k]
            mask = mk["usable"] & (mk["label_end"] < d_test)
            cnt = int(mask.sum())
            if cnt < MIN_ROWS_BLOCK:
                sizes[k] = 0
                continue
            Xk = mk["Xv"][mask]
            yk = (mk["yv"][mask] > 0).astype(int)
            mu = Xk.mean(axis=0)
            sd = Xk.std(axis=0)
            sd[sd == 0] = 1.0
            blocks_X.append((Xk - mu) / sd)
            blocks_y.append(yk)
            sizes[k] = cnt
            if k == m_name:
                mu_m, sd_m = mu, sd
        if mu_m is None or not blocks_X:
            continue                                # marche evalue pas encore utilisable
        Xtr = np.vstack(blocks_X)
        ytr = np.concatenate(blocks_y)
        if len(np.unique(ytr)) < 2:
            continue
        clf = logistic().fit(Xtr, ytr)
        if log is not None:
            log.append(dict(tr=tr, date=d_test, n_pool=len(Xtr),
                            n_own=sizes.get(m_name, 0),
                            n_markets=sum(1 for v in sizes.values() if v > 0),
                            **{f"n_{M[k]['tag']}": sizes.get(k, 0) for k in pool_names}))
        for t in range(tr, min(tr + REFIT_EVERY, n)):
            xt = Xm[t]
            if not np.all(np.isfinite(xt)):
                continue
            proba[t] = clf.predict_proba(((xt - mu_m) / sd_m).reshape(1, -1))[0, 1]
    return proba


# ------------------------------------------------- test de non-regression
# Le pooling restreint au seul marche evalue DOIT redonner exactement la
# baseline walk_forward_proba (equivalence des masques prouvee au PREREG §3.4).
print("== test de non-regression pooling(1 marche) == walk_forward_proba ==",
      file=sys.stderr)
_t = time.time()
NONREG = {}
for name, _, _ in MARKETS:
    p_ref = walk_forward_proba(M[name]["X"], M[name]["y"], logistic,
                               T0, REFIT_EVERY, EMBARGO, standardize=True)
    p_self = pooled_walk_forward(name, [name])
    both = np.isfinite(p_ref) & np.isfinite(p_self)
    same_support = bool(np.array_equal(np.isfinite(p_ref), np.isfinite(p_self)))
    max_abs = float(np.max(np.abs(p_ref[both] - p_self[both]))) if both.any() else np.nan
    NONREG[name] = dict(same_support=same_support, max_abs_diff=max_abs,
                        n_compared=int(both.sum()))
    M[name]["p_solo"] = p_ref
    print(f"   {name:<13} support identique={same_support}  "
          f"max|diff|={max_abs:.3e}  ({int(both.sum())} pts)  "
          f"[{time.time()-_t:.0f}s]", file=sys.stderr)

if not all(v["same_support"] and (not np.isfinite(v["max_abs_diff"])
                                  or v["max_abs_diff"] < 1e-9)
           for v in NONREG.values()):
    raise SystemExit("NON-REGRESSION ECHOUEE : le pooling a 1 marche ne redonne "
                     "pas la baseline -> bug a corriger AVANT tout resultat.")

# ------------------------------------------------------ candidat : 3 marches
POOL = [name for name, _, _ in MARKETS]
print("== candidat LogitL2Pooled (pool = 3 marches) ==", file=sys.stderr)
for name, _, _ in MARKETS:
    _t = time.time()
    log = []
    M[name]["p_pool"] = pooled_walk_forward(name, POOL, log=log)
    M[name]["pool_log"] = pd.DataFrame(log)
    print(f"   {name:<13} ok  ({len(log)} re-estimations, {time.time()-_t:.0f}s)",
          file=sys.stderr)


# ============================================== 3. metriques par marche
RES = {}
for name, _, _ in MARKETS:
    mm = M[name]
    n, r_fwd = mm["n"], mm["r_fwd"]
    logp = mm["logp"]
    pos = {}
    pos["BuyHold"] = np.ones(n)
    mom = (logp - logp.shift(10)).values
    pos["Momentum"] = np.where(np.isfinite(mom), np.sign(mom), 0.0)
    pos["Momentum"][pos["Momentum"] == 0] = 1.0
    pos[SOLO] = signals_from_proba(mm["p_solo"])
    pos[CAND] = signals_from_proba(mm["p_pool"])

    oos = np.arange(T0, n - 1)
    pnl = {m: backtest(pos[m], r_fwd, COST_BPS)[oos] for m in MODELS}
    metr = {m: trading_metrics(pnl[m]) for m in MODELS}
    turnover = {m: float(np.abs(np.diff(pos[m][oos], prepend=pos[m][oos][0])).mean())
                for m in MODELS}
    exposure = {m: float(np.abs(pos[m][oos]).mean()) for m in MODELS}

    ylab = (mm["yv"] > 0).astype(float)
    acc, be = {}, {}
    for m in ("Momentum", SOLO, CAND):
        p = pos[m][oos]
        valid = np.isfinite(p) & (p != 0) & np.isfinite(mm["yv"][oos])
        acc[m] = float(((p[valid] > 0).astype(float) == ylab[oos][valid]).mean())
        t_m = turnover[m]
        gross_mu = np.nanmean((pos[m] * r_fwd)[oos])
        be[m] = 1e4 * gross_mu / t_m if t_m > 0 else np.nan

    sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
    var_trials = float(np.var(list(sr_daily.values()), ddof=1))
    T_oos = len(oos)
    dsr_out = {m: dsr(sr_daily[m], T_oos, var_trials, n_trials=N_TRIALS_CUMUL,
                      skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])
               for m in MODELS}

    # ---- controle "a plat" (PREREG §2, enseignement ML-2)
    pc = pos[CAND][oos]
    flat_share = float((pc == 0).mean())
    first_bet = int(np.argmax(pc != 0)) if (pc != 0).any() else -1
    warmup_only = bool(flat_share == 0.0 or (first_bet >= 0 and (pc[first_bet:] != 0).all()))
    flat_after_warmup = float((pc[first_bet:] == 0).mean()) if first_bet >= 0 else 1.0

    # ---- critere PAR MARCHE (PREREG §5)
    bh, cd = metr["BuyHold"], metr[CAND]
    cond_a = (cd["sharpe_ann"] > bh["sharpe_ann"]) and (cd["ann_return_pct"] > bh["ann_return_pct"])
    cond_b = (np.isfinite(cd["calmar"]) and np.isfinite(bh["calmar"])
              and cd["calmar"] > bh["calmar"])
    passed = bool(cond_a or cond_b)

    np.savez(ROOT / "results" / f"ml_crossmarket_pooling_{mm['tag']}_pnl.npz",
             pos=pos[CAND][oos], pos_solo=pos[SOLO][oos], r_asset=r_fwd[oos],
             dates=np.array(mm["dates_idx"][oos].astype(str)),
             cost_bps=COST_BPS, var_trials=var_trials, n_trials=N_TRIALS_CUMUL,
             market=name)

    RES[name] = dict(metr=metr, turnover=turnover, exposure=exposure, acc=acc, be=be,
                     sr_daily=sr_daily, var_trials=var_trials, dsr=dsr_out,
                     T_oos=T_oos, oos=oos, flat_share=flat_share,
                     warmup_only=warmup_only, flat_after_warmup=flat_after_warmup,
                     cond_a=cond_a, cond_b=cond_b, passed=passed, pos=pos,
                     d0=mm["dates_idx"][oos[0]], d1=mm["dates_idx"][oos[-1]])

n_pass = sum(1 for name in RES if RES[name]["passed"])
GLOBAL_PASS = n_pass >= 2       # regle d'agregation FIXEE au PREREG §6

# ================================================================ 4. rapport
L = []
w = L.append
w("# ML-4 — Cross-market pooling : entraînement conjoint Russell 2000 / S&P 500 / DAX\n")
w("PREREG : `PREREG_ml_crossmarket_pooling.md` (committé avant tout calcul, "
  f"commit `064ae48`). Script : `scripts/{Path(__file__).name}`.\n")
w("**Dernier axe fixé a priori de la section 3 du backlog ML.**\n")

w("## 1. Définition du candidat (figée au PREREG, n_trials local = 1)\n")
w(f"- **`{CAND}`** = `LogisticRegression(C=0.5, max_iter=1000)` — "
  "**exactement** les hyperparamètres du `LogitL2` de l'Étape B officielle "
  "(`scripts/run_etape_b.py` ligne 68), repris tels quels. Aucun "
  "hyperparamètre réglé, aucun grid-search, aucune variante. **La seule chose "
  "qui change par rapport à la baseline est la composition de l'échantillon "
  "d'entraînement.**")
w("- **Pooling (PREREG §3.4)** : à chaque ré-estimation du marché évalué *m* "
  "d'indice `tr`, la ligne `i` du marché `k` (quel qu'il soit) entre dans "
  "l'entraînement **si et seulement si** sa date de fin de label "
  "`L_k[i] = date_k[min(i+H, n_k−1)]` est **strictement antérieure** à "
  "`D_test = date_m[tr]`. Purge exprimée en **dates calendaires**, jamais en "
  "indices — les calendriers de bourse US et allemand diffèrent, un embargo "
  "en indices laisserait fuir des labels étrangers dans la fenêtre de test.")
w("- **Standardisation (PREREG §3.5)** : par marché, sur les lignes "
  "d'entraînement de CE marché ; les lignes de test du marché *m* sont "
  "standardisées par `(µ_m, σ_m)`, statistiques d'entraînement de leur propre "
  "marché. Aucune statistique n'est calculée sur des données de test.")
w("- **Aucune pondération** : concaténation simple, pas de `class_weight`, pas "
  "de rééquilibrage par marché, pas de pondération par récence (PREREG §3.4-5).")
w(f"- **Features** : les {len(FEATURE_NAMES)} colonnes endogènes de "
  "`build_features(df)`, `exog=None`, calculées indépendamment sur chaque "
  "marché. Aucune feature exogène ni cross-marché (enseignement ML-2 : ce "
  "cycle teste le pooling d'**échantillons**, pas l'injection d'information "
  "contemporaine d'un marché dans un autre — déjà testée et échouée en ML-2).")
w("- **Labels** : `triple_barrier_labels(H=5, vol_span=20, mult=1,5)` calculés "
  "indépendamment par marché (barrières ∝ volatilité locale, donc "
  "automatiquement homogénéisées entre marchés de volatilités différentes).")
w(f"- **Position** : `signe(p_up − 0,5)` ∈ {{−1, +1}}, 0 pendant le warmup. "
  "**Aucun sizing probabiliste** (enseignement ML-1 : un sizing par "
  "probabilité non calibrée détruit l'exposition).")
w(f"- Walk-forward T0={T0}, refit {REFIT_EVERY} j, purge/embargo {EMBARGO} j "
  f"(forme calendaire ci-dessus), coûts {COST_BPS:.0f} bps aller-retour sur "
  "|Δposition| — **protocole de l'Étape B officielle / ML-1 / ML-2 / ML-3, "
  "non modifié**.")
w("- Fraction hors-marché rémunérée à **0 % (cash nu)** — le candidat est ±1 "
  "hors warmup, hypothèse sans effet matériel (Règle 10, PREREG §4).\n")

w("## 2. Données et contrôle qualité (Règle 7)\n")
w("| Marché | Fichier | Période | Séances | Dates dupliquées | OHLC incohérents | "
  "|Rdt| max | Fenêtre OOS (évaluation séparée) |")
w("|---|---|---|---|---|---|---|---|")
for name, path, tag in MARKETS:
    q = QREP[name]
    R = RES[name]
    w(f"| {name} | `data/{Path(path).name}` | {q['start']:%d/%m/%Y} → "
      f"{q['end']:%d/%m/%Y} | {q['n_obs']} | {q['dup_dates']} | "
      f"{q['bad_ohlc_rows']} | {q['max_abs_ret_pct']:.1f} % | "
      f"{R['d0']:%d/%m/%Y} → {R['d1']:%d/%m/%Y} ({R['T_oos']}) |")
w("")
w("*`quality_report()` lève une exception sur toute date dupliquée ou toute "
  "barre OHLC incohérente : les trois fichiers l'ont passée, sinon ce rapport "
  "n'existerait pas.*\n")

w("## 3. Test de non-régression du pooling (exigé au PREREG §3.4-3)\n")
w("Le pooling restreint au **seul marché évalué** doit redonner **exactement** "
  "la baseline `walk_forward_proba` (équivalence des masques prouvée "
  "analytiquement au PREREG : `date_m[i+5] < date_m[tr] ⟺ i ≤ tr−6 ⟺` masque "
  "`indice < tr − EMBARGO`). Vérification numérique :\n")
w("| Marché | Support des prédictions identique | max &#124;Δp_up&#124; | Points comparés |")
w("|---|---|---|---|")
for name, _, _ in MARKETS:
    v = NONREG[name]
    w(f"| {name} | {'oui' if v['same_support'] else 'NON'} | "
      f"{v['max_abs_diff']:.2e} | {v['n_compared']} |")
w("")
w("*Le pooling est donc une **extension stricte** de la baseline : tout écart "
  "observé plus bas est imputable au seul ajout des marchés étrangers dans "
  "l'échantillon d'entraînement, à aucune autre différence de code. Le script "
  "s'arrête (`SystemExit`) si ce test échoue.*\n")

w("## 4. Taille effective de l'échantillon d'entraînement (l'effet visé)\n")
w("| Marché évalué | Lignes d'entraînement (solo) — médiane | Lignes (poolé) — médiane | "
  "Facteur | Marchés contributeurs (médiane) |")
w("|---|---|---|---|---|")
for name, _, _ in MARKETS:
    lg = M[name]["pool_log"]
    med_own = float(lg["n_own"].median())
    med_pool = float(lg["n_pool"].median())
    w(f"| {name} | {med_own:,.0f} | {med_pool:,.0f} | "
      f"**×{med_pool/med_own:.2f}** | {lg['n_markets'].median():.0f} |")
w("")
w("*C'est le mécanisme même du cycle : le pooling multiplie bien la taille de "
  "l'échantillon d'apprentissage. La question du §7 est de savoir si cela se "
  "traduit en performance.*\n")

w("## 5. Performance out-of-sample par marché (nette de coûts, fenêtre propre à chaque marché)\n")
for name, _, _ in MARKETS:
    R = RES[name]
    w(f"### {name} — OOS {R['d0']:%d/%m/%Y} → {R['d1']:%d/%m/%Y} ({R['T_oos']} séances)\n")
    w("| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | "
      "Turnover moy./j | Exposition moy. | DSR (n_trials=408) |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for m in MODELS:
        x = R["metr"][m]
        w(f"| {m} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | "
          f"{x['calmar']:+.2f} | {x['ann_return_pct']:+.1f} % | "
          f"{x['max_drawdown_pct']:.1f} % | {x['profit_factor']:.2f} | "
          f"{R['turnover'][m]:.3f} | {R['exposure'][m]:.2f} | "
          f"{R['dsr'][m]['dsr']:.3f} |")
    w("")

w("*`LogitL2Solo` = le MÊME modèle entraîné sur le seul marché évalué, "
  "recalculé dans CE run (même code, mêmes labels, même graine) : c'est le "
  "contraste interne qui isole l'effet du pooling et rien d'autre.*\n")

w("## 6. Diagnostics — accuracy, break-even, turnover (JAMAIS un critère)\n")
w("Enseignement ML-3, rappelé au PREREG §2 : trois cycles consécutifs ont "
  "amélioré la *qualité* des paris sans jamais franchir Buy & Hold. Ces "
  "chiffres sont donc rapportés **à titre purement descriptif** et n'entrent "
  "dans **aucune** branche du critère du §7.\n")
w("| Marché | Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |")
w("|---|---|---|---|")
for name, _, _ in MARKETS:
    R = RES[name]
    for m in ("Momentum", SOLO, CAND):
        w(f"| {name} | {m} | {100*R['acc'][m]:.2f} % | {R['be'][m]:+.2f} |")
w("")

w("## 7. Contrôle de couverture « à plat » (PREREG §2, enseignement ML-2)\n")
w("Chaque marché est évalué sur SA PROPRE fenêtre de test, définie par SON "
  "PROPRE historique : la couverture est de 100 % par construction. Contrôle "
  "opérationnel exigé d'avance : **0,00 % de séances à plat hors warmup**.\n")
w("| Marché | Part OOS à plat (position 0) | Part à plat APRÈS le 1er pari | "
  "Exclusivement le warmup |")
w("|---|---|---|---|")
for name, _, _ in MARKETS:
    R = RES[name]
    w(f"| {name} | {100*R['flat_share']:.2f} % | "
      f"{100*R['flat_after_warmup']:.2f} % | "
      f"{'oui' if R['warmup_only'] else 'NON — anomalie à investiguer'} |")
w("")
w("*L'artefact de ML-2 (candidat à plat sur 30,7 % de l'OOS faute d'historique "
  "exogène) n'est pas reproduit : l'historique DAX borné au 01/11/1999 "
  "n'affecte que la **composition du pool d'entraînement** des autres marchés "
  "aux dates anciennes (§4), jamais une fenêtre de test.*\n")

w("## 8. Verdict par marché (critère chiffré du PREREG §5)\n")
w("| Marché | (A) Sharpe ET rendement > BuyHold | (B) Calmar > BuyHold | Verdict marché |")
w("|---|---|---|---|")
for name, _, _ in MARKETS:
    R = RES[name]
    cd, bh = R["metr"][CAND], R["metr"]["BuyHold"]
    w(f"| {name} | {cd['sharpe_ann']:+.2f} vs {bh['sharpe_ann']:+.2f} et "
      f"{cd['ann_return_pct']:+.1f} % vs {bh['ann_return_pct']:+.1f} % → "
      f"**{'satisfait' if R['cond_a'] else 'NON'}** | "
      f"{cd['calmar']:+.2f} vs {bh['calmar']:+.2f} → "
      f"**{'satisfait' if R['cond_b'] else 'NON'}** | "
      f"**{'PASS niveau 1' if R['passed'] else 'FAIL'}** |")
w("")

w("## 9. Verdict global (règle d'agrégation FIXÉE AU PREREG §6, avant tout calcul)\n")
w("Règle pré-enregistrée : **PASS niveau 1 global si et seulement si au moins "
  "2 marchés sur 3 passent**. Justification écrite d'avance : évaluer 3 marchés "
  "c'est se donner 3 chances (une règle « 1 sur 3 suffit » contredirait la "
  "Règle 2), tandis qu'exiger 3/3 serait excessivement sévère vu l'historique "
  "plus court du DAX ; l'hypothèse testée est que le pooling **généralise**, "
  "et la majorité stricte en est la traduction fidèle.\n")
w(f"**Marchés passant le critère : {n_pass} / 3.**\n")
w(f"### {'PASS niveau 1 (global)' if GLOBAL_PASS else 'FAIL niveau 1 (global)'}\n")
for name, _, _ in MARKETS:
    R = RES[name]
    cd, sl, bh = R["metr"][CAND], R["metr"][SOLO], R["metr"]["BuyHold"]
    w(f"- **{name}** — effet du pooling sur le MÊME modèle : Sharpe "
      f"{sl['sharpe_ann']:+.2f} → {cd['sharpe_ann']:+.2f} "
      f"({cd['sharpe_ann']-sl['sharpe_ann']:+.2f}), rendement annualisé "
      f"{sl['ann_return_pct']:+.1f} % → {cd['ann_return_pct']:+.1f} %, MDD "
      f"{sl['max_drawdown_pct']:.1f} % → {cd['max_drawdown_pct']:.1f} %, "
      f"accuracy {100*R['acc'][SOLO]:.2f} % → {100*R['acc'][CAND]:.2f} %, "
      f"turnover {R['turnover'][SOLO]:.3f} → {R['turnover'][CAND]:.3f}/j. "
      f"Benchmark BuyHold du même marché : {bh['sharpe_ann']:+.2f} / "
      f"{bh['ann_return_pct']:+.1f} % / Calmar {bh['calmar']:+.2f}.")
w("")
if GLOBAL_PASS:
    w("Ce PASS est un **niveau 1 uniquement**. Il n'a de valeur qu'après la "
      "batterie de validation renforcée (§2.4 du backlog ML, 5 contrôles a-e), "
      "exécutée **séparément par marché** — `spa_test` compare un candidat à UN "
      "SEUL benchmark partagé, aucun SPA joint multi-marchés n'est tenté "
      "(limite mécanique déjà rencontrée aux cycles non-ML #150/#159). Voir "
      "`ml_crossmarket_pooling_battery.md`. Aucune notification n'est émise sur "
      "un PASS niveau 1 seul.")
elif n_pass == 1:
    w("Le critère global n'est pas atteint (1 marché sur 3, la règle "
      "pré-enregistrée en exige 2). Conformément à la **clause complémentaire "
      "du PREREG §6**, la batterie renforcée est tout de même exécutée sur le "
      "marché passant, à titre documentaire — cela ne change PAS le verdict "
      "global, qui reste FAIL niveau 1.")
else:
    w("Le critère pré-enregistré n'est atteint sur aucun marché : **pooler "
      "l'échantillon d'entraînement de 3 marchés génétiquement indépendants ne "
      "suffit pas** à faire passer le modèle directionnel au-dessus de Buy & "
      "Hold. La batterie de validation renforcée n'est pas déclenchée (elle ne "
      "s'applique qu'à un PASS niveau 1). Résultat rapporté tel quel, sans "
      "changement rétroactif du critère, de la règle d'agrégation ou de "
      "l'univers de marchés.")
w("")

w("## 10. Deflated Sharpe Ratio\n")
w(f"`n_trials = {N_TRIALS_CUMUL}` = 400 (brute-force ML 1-10, closes) + 4 "
  "(univers figé Étape B) + 1 (ML-1) + 1 (ML-2) + 1 (ML-3) + 1 (ce cycle "
  "ML-4). **Jamais réduit à 1** (Règle 2). DSR calculé **séparément par "
  "marché** (jamais sur une série poolée) ; `var_trials` = variance des Sharpe "
  "quotidiens des 4 signaux du marché concerné.\n")
w("| Marché | σ²(SR quot.) | DSR BuyHold | DSR LogitL2Solo | DSR LogitL2Pooled |")
w("|---|---|---|---|---|")
for name, _, _ in MARKETS:
    R = RES[name]
    w(f"| {name} | {R['var_trials']:.3e} | {R['dsr']['BuyHold']['dsr']:.3f} | "
      f"{R['dsr'][SOLO]['dsr']:.3f} | **{R['dsr'][CAND]['dsr']:.3f}** |")
w("")

w("## 11. Traçabilité (Règle 6)\n")
w(f"- Script : `finance/trading/scripts/{Path(__file__).name}` — "
  "toute statistique de ce rapport en sort directement.")
w("- Positions OOS sauvegardées pour audit : "
  + ", ".join(f"`results/ml_crossmarket_pooling_{M[n]['tag']}_pnl.npz`"
              for n, _, _ in MARKETS) + ".")
w("- PREREG : `PREREG_ml_crossmarket_pooling.md`, commit `064ae48`, antérieur "
  "à toute exécution de ce script.")
w(f"- Commande : `python3 finance/trading/scripts/{Path(__file__).name}`.")

Path(OUT).parent.mkdir(parents=True, exist_ok=True)
Path(OUT).write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"\n== ecrit : {OUT}", file=sys.stderr)
print(f"== marches passant le critere : {n_pass}/3 -> "
      f"{'PASS niveau 1 global' if GLOBAL_PASS else 'FAIL niveau 1 global'}",
      file=sys.stderr)
for name, _, _ in MARKETS:
    R = RES[name]
    print(f"   {name:<13} {'PASS' if R['passed'] else 'FAIL'}  "
          f"cand Sharpe={R['metr'][CAND]['sharpe_ann']:+.2f} "
          f"rdt={R['metr'][CAND]['ann_return_pct']:+.1f}% "
          f"calmar={R['metr'][CAND]['calmar']:+.2f} | "
          f"BH Sharpe={R['metr']['BuyHold']['sharpe_ann']:+.2f} "
          f"rdt={R['metr']['BuyHold']['ann_return_pct']:+.1f}% "
          f"calmar={R['metr']['BuyHold']['calmar']:+.2f}", file=sys.stderr)
