"""Backtest cross-market — meilleur pipeline NDX (LogitL2 + overlay optimise)
applique tel quel a 3 indices externes (Russell 2000, S&P 500, DAX).
Produit results/backtest_indices.md.

Objectif (cf. CLAUDE.md, Etape D "en cours") : le pipeline LogitL2 (Etape B) +
overlay vol-targeting GJR-GARCH(1,1)-t (cap 2.0x, coupe totale au 90e
percentile in-sample - meilleure combinaison du grid-search fige,
cf. results/etape_D_overlay_optimized.md et src/integrated_pipeline.py) a ete
valide sur NDX (40 ans). Ce script verifie s'il se GENERALISE a d'autres
marches/indices, sans aucun re-reglage : memes hyperparametres, meme
protocole, aucune optimisation specifique a chaque nouvel indice (sinon
data-snooping).

Univers de donnees FIGE (3 indices, aucun ajout a posteriori) :
  1. Russell 2000 (^RUT, small-cap US)   -> data/russell2000_daily.txt
  2. S&P 500 (^GSPC, large-cap US)       -> data/sp500_daily.txt
  3. DAX (^GDAXI, large-cap Allemagne)   -> data/dax_daily.txt
Telecharges depuis Yahoo Finance (chart API publique, aucune cle requise),
nettoyage minimal (clamp OHLC, coupe avant la premiere date a volume non
nul = ere de cotation fiable), valides par data_loader.quality_report (0
doublon, 0 ligne OHLC incoherente) - cf. scripts/fetch_index_data.py.

PROTOCOLE FIGE (identique NDX, aucun parametre retouche) :
  T0=750, refit 21 j (primaire LogitL2 ET overlay GJR-t), embargo 5 j,
  triple barrier H=5 j / +-1.5*sigma_local (ewm 20 j), couts 5 bps
  aller-retour, overlay cap 2.0x / coupe totale au 90e percentile in-sample
  (EXTREME_CUT_FRAC=0.0, cf. src/overlay.py).

Univers de 3 variantes EXACTEMENT par indice (aucun ajout a posteriori,
N=3 pour le DSR - calcule PAR INDICE, jamais combine entre indices, cf.
CLAUDE.md discipline anti data-snooping) :
  1. Buy & Hold           - reference
  2. LogitL2 seul          - Etape B, signal actif meilleur DSR sur NDX
  3. LogitL2 + Overlay     - Etape B x exposition vol-targeting (cap 2.0x,
                             coupe 90e pctl) - meilleure combinaison NDX

CRITERE DE SUCCES (fixe a priori, cf. CLAUDE.md/tache) : le pipeline
LogitL2+Overlay reduit le MDD vs Buy & Hold sur >= 2/3 indices de facon
MATERIELLE (>20% relatif), sans perdre l'essentiel du rendement (>=80% du
rendement annualise Buy & Hold). Verifie ci-dessous, pas suppose.
"""
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import EXTREME_CUT_FRAC, extreme_cut, vol_target_exposure, walk_forward_vol_forecast  # noqa: E402
from prediction import (  # noqa: E402
    backtest,
    build_features,
    dsr,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_proba,
)

# ------------------------------------------------------------------ protocole
# FIGE, identique a NDX (src/integrated_pipeline.py) - aucun parametre retouche
# par indice.
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
OVERLAY_CAP = 2.0
OVERLAY_PCTL = 90.0
SEED = 42

VARIANTS = ["BuyHold", "LogitL2", "LogitL2+Overlay"]

# Univers de 3 indices FIGE (cf. docstring), aucun ajout a posteriori.
INDICES = [
    ("Russell 2000 (^RUT, small-cap US)", ROOT / "data" / "russell2000_daily.txt"),
    ("S&P 500 (^GSPC, large-cap US)", ROOT / "data" / "sp500_daily.txt"),
    ("DAX (^GDAXI, large-cap Allemagne)", ROOT / "data" / "dax_daily.txt"),
]

OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "backtest_indices.md")


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def run_one(label: str, path: Path) -> dict:
    df_raw = load_ohlc(str(path))
    quality_report(df_raw)  # leve si donnees corrompues (0 doublon, 0 OHLC incoherent attendu)
    df = df_raw.set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r_fwd = (logp.shift(-1) - logp).values  # rendement futur t->t+1
    n = len(df)
    dates = df.index

    assert n > T0 + REFIT_EVERY, f"{label} : historique trop court pour T0={T0}"

    # --- 1) Primaire LogitL2 (Etape B, walk-forward purge/embargo, inchange)
    X = build_features(df)
    y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
    y.index = df.index
    p_up = walk_forward_proba(X, y, logistic, T0, REFIT_EVERY, EMBARGO, standardize=True)
    pos_primary = np.where(np.isfinite(p_up), np.where(p_up > 0.5, 1.0, -1.0), 0.0)

    # --- 2) Overlay vol-targeting GJR-t (cap 2.0x, coupe 90e pctl in-sample, coupe totale)
    # Meme convention que src/integrated_pipeline.py : r_pct (rendements log %, longueur
    # n-1) et r_fwd (longueur n, derniere valeur NaN) partagent les memes valeurs
    # numeriques aux memes positions t < n-1 ; l'exposition est completee a la longueur
    # n par 0 (derniere position jamais evaluee dans l'OOS = arange(T0, n-1)).
    r_pct = log_returns_pct(df_raw).values
    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY, extreme_pctl=OVERLAY_PCTL)
    expo = vol_target_exposure(fc["vol_fcst"], fc["vol_target"], OVERLAY_CAP)
    expo = extreme_cut(expo, fc["vol_fcst"], fc["vol_thresh"], EXTREME_CUT_FRAC)
    exposure = np.nan_to_num(expo, nan=0.0)
    exposure = np.concatenate([exposure, [0.0]])

    positions = {
        "BuyHold": np.ones(n),
        "LogitL2": pos_primary,
        "LogitL2+Overlay": pos_primary * exposure,
    }

    # fenetre OOS commune (a partir de T0, la ou tous les modeles decident ; -1 :
    # r_fwd[n-1] est NaN, pas de lendemain)
    oos = np.arange(T0, n - 1)
    T_oos = len(oos)
    n_years = (dates[oos[-1]] - dates[oos[0]]).days / 365.25

    pnl = {m: backtest(positions[m], r_fwd, COST_BPS)[oos] for m in VARIANTS}
    metr = {m: trading_metrics(pnl[m]) for m in VARIANTS}

    # DSR PAR INDICE (N=3, jamais combine entre indices - discipline anti data-snooping)
    sr_daily = {m: metr[m]["sharpe_daily"] for m in VARIANTS}
    var_trials = float(np.var(list(sr_daily.values()), ddof=1))
    dsr_out = {
        m: dsr(sr_daily[m], T_oos, var_trials, n_trials=len(VARIANTS),
               skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])
        for m in VARIANTS
    }

    turnover = {m: float(np.mean(np.abs(np.diff(positions[m][oos], prepend=positions[m][oos][0]))))
               for m in VARIANTS}

    bh = metr["BuyHold"]
    ov = metr["LogitL2+Overlay"]
    mdd_reduction = 1.0 - abs(ov["max_drawdown_pct"]) / abs(bh["max_drawdown_pct"]) if bh["max_drawdown_pct"] != 0 else np.nan
    ret_ratio = ov["ann_return_pct"] / bh["ann_return_pct"] if bh["ann_return_pct"] != 0 else np.nan
    material = bool(mdd_reduction > 0.20)
    keeps_return = bool(ret_ratio >= 0.80)

    return {
        "label": label, "path": path, "n": n, "T_oos": T_oos, "n_years": n_years,
        "dates_oos": (dates[oos[0]], dates[oos[-1]]),
        "metr": metr, "dsr": dsr_out, "turnover": turnover,
        "mdd_reduction": mdd_reduction, "ret_ratio": ret_ratio,
        "material": material, "keeps_return": keeps_return,
    }


results = []
for label, path in INDICES:
    print(f"=== {label} ===", flush=True)
    results.append(run_one(label, path))

# ------------------------------------------------------------------------ rapport
lines = []
w = lines.append
w("# Backtest cross-market — LogitL2 + overlay (NDX) sur 3 indices externes\n")
w("Valide si le meilleur pipeline trouvé sur NDX (LogitL2, Étape B, + overlay "
  "vol-targeting GJR-GARCH(1,1)-t cap 2.0×/coupe totale au 90e percentile "
  "in-sample, meilleure combinaison du grid-search figé — "
  "`results/etape_D_overlay_optimized.md`) se **généralise** à d'autres "
  "marchés, **sans aucun re-réglage** (mêmes hyperparamètres partout).\n")
w(f"**Protocole figé** (identique NDX) : fenêtre initiale {T0} obs "
  f"expansive, ré-estimation tous les {REFIT_EVERY} j (primaire LogitL2 et "
  f"overlay GJR-t), purge/embargo {EMBARGO} j, triple barrier H={H} j "
  f"±{BARRIER_MULT}·σ_local (ewm {VOL_SPAN} j), coûts {COST_BPS:.0f} bps "
  f"aller-retour, overlay cap {OVERLAY_CAP:.1f}×/coupe totale au "
  f"{OVERLAY_PCTL:.0f}e percentile in-sample.\n")
w("**Univers figé** : 3 indices externes (Russell 2000, S&P 500, DAX) × 3 "
  "variantes (Buy & Hold, LogitL2, LogitL2+Overlay) = 9 tests, aucun ajout "
  "a posteriori. Le DSR est calculé **par indice** (N=3, familles non "
  "combinées entre indices — cf. discipline anti-data-snooping).\n")

w("## Données\n")
w("| Indice | Fichier | Séances | Période complète | OOS |")
w("|---|---|---|---|---|")
for r in results:
    df_full = load_ohlc(str(r["path"]))
    w(f"| {r['label']} | `{r['path'].name}` | {r['n']} | "
      f"{df_full['date'].iloc[0]:%d/%m/%Y} → {df_full['date'].iloc[-1]:%d/%m/%Y} | "
      f"{r['dates_oos'][0]:%d/%m/%Y} → {r['dates_oos'][1]:%d/%m/%Y} "
      f"({r['T_oos']} obs, ~{r['n_years']:.1f} ans) |")
w("")

for r in results:
    w(f"## {r['label']}\n")
    w("| Variante | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | "
      "Rdt ann. % | Turnover | DSR (N=3) |")
    w("|---|---|---|---|---|---|---|---|")
    for m in VARIANTS:
        me = r["metr"][m]
        w(f"| {m} | {me['sharpe_ann']:+.2f} | {me['sortino_ann']:+.2f} | "
          f"{me['calmar']:+.2f} | {me['max_drawdown_pct']:.1f} | "
          f"{me['ann_return_pct']:+.1f} | {r['turnover'][m]:.3f} | "
          f"{r['dsr'][m]['dsr']:.3f} |")
    w("")
    w(f"- **LogitL2+Overlay vs Buy & Hold** : réduction MDD relative = "
      f"{100*r['mdd_reduction']:+.1f}% (seuil >20%), rendement ann. conservé "
      f"= {100*r['ret_ratio']:.1f}% du Buy & Hold (seuil ≥80%) → "
      + ("**matériel**" if r["material"] else "non matériel")
      + " / "
      + ("**rendement conservé**" if r["keeps_return"] else "rendement NON conservé")
      + ".\n")

# ------------------------------------------------------------------------ verdict
n_success = sum(1 for r in results if r["material"] and r["keeps_return"])
n_material = sum(1 for r in results if r["material"])
overall_ok = n_success >= 2

w("## Verdict cross-market\n")
w("Critère de succès (fixé a priori) : le pipeline LogitL2+Overlay réduit le "
  "MDD vs Buy & Hold sur **au moins 2/3 indices** de façon matérielle (>20% "
  "relatif), sans perdre l'essentiel du rendement (≥80% de Buy & Hold).\n")
w("| Indice | ΔMDD relatif | Rdt ann. / BuyHold | Matériel (>20%) | Rendement conservé (≥80%) | Succès combiné |")
w("|---|---|---|---|---|---|")
for r in results:
    ok = r["material"] and r["keeps_return"]
    w(f"| {r['label']} | {100*r['mdd_reduction']:+.1f}% | {100*r['ret_ratio']:.1f}% | "
      f"{'OUI' if r['material'] else 'non'} | {'OUI' if r['keeps_return'] else 'non'} | "
      f"{'**OUI**' if ok else 'NON'} |")
w("")
w(f"**{n_success}/3 indices** remplissent le critère de succès complet "
  f"(réduction MDD matérielle ET rendement conservé) ; {n_material}/3 "
  "atteignent au moins la réduction de MDD matérielle seule.\n")

if overall_ok:
    w("**Verdict honnête : le critère de généralisation cross-market est "
      f"ATTEINT** ({n_success}/3 ≥ 2/3 indices). Le pipeline LogitL2+overlay "
      "(hyperparamètres figés sur NDX, non re-réglés ici) réduit le "
      "drawdown de façon matérielle sur la majorité des indices testés sans "
      "sacrifier l'essentiel du rendement Buy & Hold — un signe de "
      "robustesse au-delà du seul NDX, même si la magnitude varie d'un "
      "marché à l'autre (cf. tableaux ci-dessus). Rappel anti-data-snooping "
      ": aucun paramètre n'a été ré-optimisé par indice ; c'est précisément "
      "ce test de généralisation, sans triche, qui donne sa valeur au "
      "résultat.")
else:
    w("**Verdict honnête : le critère de généralisation cross-market N'EST "
      f"PAS atteint** ({n_success}/3 < 2/3 indices). Le pipeline "
      "LogitL2+overlay, calibré sur NDX et appliqué tel quel (aucun "
      "re-réglage), ne réduit pas le drawdown de façon matérielle sur la "
      "majorité des indices externes testés, ou le fait au prix d'une perte "
      "de rendement trop importante. Ce résultat est rapporté tel quel : il "
      "suggère que le réglage cap 2.0×/coupe 90e percentile trouvé sur NDX "
      "est en partie spécifique à cet historique (40 ans, incluant "
      "2000-2002) plutôt qu'un réglage universel — cohérent avec la mise en "
      "garde déjà faite en Étape D (grid-search) sur la non-généralisation "
      "automatique des paramètres optimisés.")

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))
