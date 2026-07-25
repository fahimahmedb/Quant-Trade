"""Backtest cross-marche : le pipeline LogitL2 + overlay (retenu sur NDX,
cf. `finance/trading/results/etape_D_overlay_optimized.md` et
`results/integrated_pipeline.md`) se generalise-t-il a d'autres indices ?

Produit `results/backtest_indices.md` (3 tableaux, un par indice, + verdict
cross-market).

NOTE DE LOCALISATION (repo reorganise, cf. commit "Reorganize repository:
finance/trading, divers/robot-politique, cours") : les modules reutilises
(data_loader, prediction, overlay, meta_labeling pour la factory LogitL2)
vivent sous finance/src/, pas src/ a la racine. Ce script (racine scripts/,
conforme au chemin demande dans la tache) importe donc depuis finance/src/
explicitement ci-dessous, comme scripts/run_integrated_pipeline.py.

PROTOCOLE FIGE (IDENTIQUE a NDX, cf. CLAUDE.md Etape B/D et
`finance/src/integrated_pipeline.py` - aucun parametre retouche) :
  - T0=750, refit tous les 21 j (fenetre expansive), purge/embargo=5 j
  - labels triple barrier H=5 j, +/-1.5*sigma_ewm20
  - couts 5 bps aller-retour
  - overlay : GJR-GARCH(1,1)-t vol-targeting, cap 2.0x, coupe totale (frac=0)
    au-dela du 90e percentile in-sample de la vol prevue (meilleure
    combinaison retenue sur NDX, cf. etape_D_overlay_optimized.md ;
    PAS re-optimisee ici - reutilisee telle quelle sur les 3 indices).

NOTE DE COHERENCE PROTOCOLE : la tache demande explicitement "T0=750, refit
21j, embargo 5j" (identique a l'etude NDX deja publiee dans le repo, cf.
integrated_pipeline.py: T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5). Un
message ulterieur de la meme conversation mentionnait "embargo 21j" et des
strategies non documentees dans CLAUDE.md ("R5_FracDiff", "H12") qui ne
figurent PAS dans les "resultats deja etablis" du fichier de contexte du
projet et proviennent visiblement de scripts hors-discipline a la racine
du repo (HYPOTHESIS_TESTING_RESULTS.md, etc., absents de CLAUDE.md). Ce
script suit le protocole EXPLICITE et DETAILLE de la tache ("Protocole
fige" ci-dessus), identique a celui deja fige et publie pour NDX - c'est la
seule maniere de comparer les resultats indices-vs-NDX comme demande
("valider que le meilleur pipeline trouve sur NDX ... se generalise").

UNIVERS FIGE (anti data-snooping) : 3 indices (Russell 2000, S&P 500, DAX) x
3 variantes (BuyHold, LogitL2, LogitL2+Overlay) = 9 tests EXACTEMENT, aucun
ajout a posteriori. DSR : n_trials=3 PAR INDICE (les 3 variantes de cet
indice), jamais combine statistiquement entre indices (cf. tache).
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "finance" / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from meta_labeling import SECONDARY_MODELS  # noqa: E402
from overlay import extreme_cut, vol_target_exposure, walk_forward_vol_forecast  # noqa: E402
from prediction import (  # noqa: E402
    backtest,
    build_features,
    dsr,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_proba,
)

# --------------------------------------------------------------- protocole FIGE
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
OVERLAY_CAP = 2.0
OVERLAY_PCTL = 90.0
EXTREME_CUT_FRAC = 0.0  # coupe totale, identique a etape_D_overlay_optimized.md

VARIANTS = ["BuyHold", "LogitL2", "LogitL2+Overlay"]  # univers fige, n_trials=3/indice

# Seuils de succes DECLARES AVANT lecture des resultats (cf. tache) :
MDD_REDUCTION_THRESHOLD = 0.20   # reduction relative du MDD, Overlay vs BuyHold
RET_KEEP_THRESHOLD = 0.80        # rendement annualise conserve (Overlay / BuyHold)
N_SUCCESS_REQUIRED = 2           # sur 3 indices

INDICES = [
    ("Russell 2000", ROOT / "data" / "russell2000_daily.txt"),
    ("S&P 500", ROOT / "data" / "sp500_daily.txt"),
    ("DAX", ROOT / "data" / "dax_daily.txt"),
]

# Reference NDX deja publiee (results/integrated_pipeline.md, meme protocole
# exact) - rappelee a titre de comparaison, PAS recalculee ici.
NDX_REF = {
    "OOS": "9522 j (19/09/1988 -> 10/07/2026)",
    "BuyHold": {"sharpe_ann": 0.52, "calmar": 0.08, "mdd": -82.9, "ret": 14.5},
    "LogitL2": {"sharpe_ann": 0.35, "calmar": 0.10, "mdd": -59.6, "ret": 9.5},
    "LogitL2+Overlay": {"sharpe_ann": 0.44, "calmar": 0.13, "mdd": -52.4, "ret": 10.2},
}

OUT = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "results" / "backtest_indices.md")


def primary_logit():
    """Modele primaire LogitL2, identique a l'Etape B / integrated_pipeline.py."""
    return SECONDARY_MODELS["LogitL2"]()


def build_pipeline_3variant(df_raw) -> dict:
    """Version allegee de finance/src/integrated_pipeline.py::build_pipeline,
    limitee aux 3 variantes de cette tache (pas de meta-labeling - hors
    perimetre ici). Reutilise EXACTEMENT les memes briques deja validees
    (build_features, triple_barrier_labels, walk_forward_proba, overlay
    GJR-t) et les memes valeurs de parametres (cap 2.0x, coupe 90e pctl)."""
    df = df_raw.set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r_fwd = (logp.shift(-1) - logp).values
    n = len(df)
    dates = df.index

    # --- 1) Primaire LogitL2 (Etape B, walk-forward purge/embargo, inchange)
    X = build_features(df)
    y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
    y.index = df.index
    p_up = walk_forward_proba(X, y, primary_logit, T0, REFIT_EVERY, EMBARGO, standardize=True)
    pos_primary = np.where(np.isfinite(p_up), np.where(p_up > 0.5, 1.0, -1.0), 0.0)

    # --- 2) Overlay vol-targeting GJR-t (cap 2.0x, coupe 90e pctl in-sample, coupe totale)
    r_pct = log_returns_pct(df_raw).values
    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY, extreme_pctl=OVERLAY_PCTL)
    expo = vol_target_exposure(fc["vol_fcst"], fc["vol_target"], OVERLAY_CAP)
    expo = extreme_cut(expo, fc["vol_fcst"], fc["vol_thresh"], EXTREME_CUT_FRAC)
    exposure = np.nan_to_num(expo, nan=0.0)
    exposure = np.concatenate([exposure, [0.0]])  # complete a longueur n (derniere pos jamais evaluee)

    positions = {
        "BuyHold": np.ones(n),
        "LogitL2": pos_primary,
        "LogitL2+Overlay": pos_primary * exposure,
    }
    return {"positions": positions, "r_fwd": r_fwd, "dates": dates, "n": n}


def block_bootstrap_sharpe_ci(strat_ret: np.ndarray, ann: int = 252, n_boot: int = 2000,
                              block: int = 20, seed: int = 0) -> tuple:
    """IC 95% du Sharpe annualise par block-bootstrap stationnaire (blocs de
    `block` jours, pour respecter l'autocorrelation/heteroscedasticite -
    jamais un bootstrap i.i.d. sur des rendements financiers)."""
    rng = np.random.default_rng(seed)
    r = strat_ret[np.isfinite(strat_ret)]
    n = len(r)
    if n < block * 2:
        return (np.nan, np.nan)
    n_blocks = int(np.ceil(n / block))
    sharpes = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, n - block, size=n_blocks)
        sample = np.concatenate([r[s:s + block] for s in starts])[:n]
        mu, sd = sample.mean(), sample.std(ddof=1)
        sharpes[b] = (mu / sd * np.sqrt(ann)) if sd > 0 else 0.0
    return (float(np.percentile(sharpes, 2.5)), float(np.percentile(sharpes, 97.5)))


def run_one_index(name: str, path: Path) -> dict:
    print(f"\n=== {name} ({path.name}) ===")
    t_start = time.time()
    df_raw = load_ohlc(str(path))
    rep = quality_report(df_raw)
    print(f"  {rep['n_obs']} seances, {rep['start']:%d/%m/%Y} -> {rep['end']:%d/%m/%Y}, "
          f"{rep['dup_dates']} doublons, {rep['bad_ohlc_rows']} lignes OHLC incoherentes")

    out = build_pipeline_3variant(df_raw)
    positions, r_fwd, dates, n = out["positions"], out["r_fwd"], out["dates"], out["n"]
    oos = np.arange(T0, n - 1)
    T_oos = len(oos)

    pnl = {v: backtest(positions[v], r_fwd, COST_BPS)[oos] for v in VARIANTS}
    metr = {v: trading_metrics(pnl[v]) for v in VARIANTS}
    turnover = {v: float(np.abs(np.diff(positions[v][oos], prepend=positions[v][oos][0])).mean())
                for v in VARIANTS}
    ci95 = {v: block_bootstrap_sharpe_ci(pnl[v]) for v in VARIANTS}

    sr_daily = {v: metr[v]["sharpe_daily"] for v in VARIANTS}
    var_trials = float(np.var(list(sr_daily.values()), ddof=1))
    n_trials = len(VARIANTS)  # =3, PAR INDICE (cf. discipline anti-snooping, jamais combine)
    dsr_out = {v: dsr(sr_daily[v], T_oos, var_trials, n_trials,
                      skew=metr[v]["skew"], kurt_excess=metr[v]["excess_kurt"])
               for v in VARIANTS}

    base = metr["BuyHold"]
    combo = metr["LogitL2+Overlay"]
    mdd_base, mdd_combo = abs(base["max_drawdown_pct"]), abs(combo["max_drawdown_pct"])
    mdd_reduction = 1.0 - mdd_combo / mdd_base if mdd_base > 0 else np.nan
    ret_ratio = (combo["ann_return_pct"] / base["ann_return_pct"]
                if base["ann_return_pct"] != 0 else np.nan)
    success = bool(np.isfinite(mdd_reduction) and mdd_reduction > MDD_REDUCTION_THRESHOLD
                  and np.isfinite(ret_ratio) and ret_ratio >= RET_KEEP_THRESHOLD)

    print(f"  OOS={T_oos} j ({dates[oos[0]]:%d/%m/%Y} -> {dates[oos[-1]]:%d/%m/%Y}) "
          f"- termine en {time.time()-t_start:.0f}s")
    for v in VARIANTS:
        print(f"    {v:18s} Sharpe={metr[v]['sharpe_ann']:+.2f} MDD={metr[v]['max_drawdown_pct']:.1f}% "
              f"Rdt={metr[v]['ann_return_pct']:+.1f}% DSR={dsr_out[v]['dsr']:.3f}")

    return {
        "name": name, "rep": rep, "metr": metr, "turnover": turnover, "ci95": ci95,
        "dsr": dsr_out, "var_trials": var_trials, "T_oos": T_oos,
        "dates_oos": (dates[oos[0]], dates[oos[-1]]),
        "mdd_reduction": mdd_reduction, "ret_ratio": ret_ratio, "success": success,
    }


def fmt_pct(x):
    return f"{x:+.1f} %" if np.isfinite(x) else "n/a"


def main():
    results = []
    for name, path in INDICES:
        results.append(run_one_index(name, path))

    n_success = sum(r["success"] for r in results)
    overall_success = n_success >= N_SUCCESS_REQUIRED

    lines = []
    w = lines.append
    w("# Backtest cross-marché — pipeline LogitL2 + overlay (validation NDX → 3 indices)\n")

    w("## 1. Cadrage\n")
    w("Objectif : vérifier que le meilleur pipeline trouvé sur NDX — signal "
      "primaire **LogitL2** (Étape B) combiné à l'**overlay** de gestion du "
      "risque GJR-GARCH(1,1)-t vol-targeting (cap 2.0×, coupe totale au-delà "
      "du 90e percentile in-sample de la vol prévue ; cf. "
      "`finance/trading/results/etape_D_overlay_optimized.md`) — se "
      "**généralise** à d'autres marchés/indices, ou s'il est spécifique à NDX "
      "(surapprentissage de marché).\n")
    w(f"**Protocole figé, identique à l'étude NDX déjà publiée** "
      f"(`results/integrated_pipeline.md`, `finance/src/integrated_pipeline.py`) : "
      f"walk-forward T0={T0}, ré-estimation tous les {REFIT_EVERY} j, "
      f"purge/embargo {EMBARGO} j, labels triple barrier H={H} j "
      f"±{BARRIER_MULT}·σ_ewm{VOL_SPAN}, coûts {COST_BPS:.0f} bps aller-retour. "
      f"Overlay : cap {OVERLAY_CAP:.1f}×, coupe {OVERLAY_PCTL:.0f}e percentile "
      "— **aucun paramètre ré-optimisé** sur les 3 indices ci-dessous, ce sont "
      "ceux déjà retenus sur NDX, réutilisés tels quels (test de "
      "généralisation, pas un nouveau grid-search).\n")
    w("**Note de cohérence de protocole** : la tâche a spécifié explicitement "
      "« T0=750, refit 21j, embargo 5j » dans son \"Protocole figé\" détaillé, "
      "identique au protocole déjà figé et publié pour NDX "
      "(`integrated_pipeline.py`: `T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5`). "
      "Un message ultérieur de la même conversation mentionnait un embargo de "
      "21 j et des stratégies (« R5_FracDiff », « H12 ») absentes des "
      "« résultats déjà établis » de `CLAUDE.md` — elles proviennent "
      "visiblement de scripts hors discipline anti-data-snooping trouvés à la "
      "racine du repo (`HYPOTHESIS_TESTING_RESULTS.md`, etc.), pas de la "
      "chaîne A→B→C→D documentée. Ce script suit le protocole détaillé et "
      "déjà validé (embargo=5j) : c'est la seule option cohérente avec la "
      "comparaison directe aux chiffres NDX déjà publiés, demandée par la "
      "tâche.\n")
    w("**Univers figé (anti data-snooping)** : 3 indices × 3 variantes = 9 "
      "tests exactement, aucun ajout a posteriori. Le DSR (Deflated Sharpe "
      "Ratio) est calculé avec **n_trials=3 par indice** (famille des 3 "
      "variantes de CET indice) — jamais combiné statistiquement entre "
      "indices, comme demandé.\n")

    w("## 2. Référence NDX (déjà publiée, rappelée pour comparaison — pas recalculée ici)\n")
    w(f"OOS NDX : {NDX_REF['OOS']}.\n")
    w("| Variante | Sharpe ann. | Calmar | MDD | Rdt ann. |")
    w("|---|---|---|---|---|")
    for v in VARIANTS:
        x = NDX_REF[v]
        w(f"| {v} | {x['sharpe_ann']:+.2f} | {x['calmar']:+.2f} | {x['mdd']:.1f} % | {x['ret']:+.1f} % |")
    ndx_mdd_red = 1 - abs(NDX_REF["LogitL2+Overlay"]["mdd"]) / abs(NDX_REF["BuyHold"]["mdd"])
    ndx_ret_ratio = NDX_REF["LogitL2+Overlay"]["ret"] / NDX_REF["BuyHold"]["ret"]
    w(f"\nSur NDX : réduction MDD (Overlay vs BuyHold) = **{100*ndx_mdd_red:+.1f} %** "
      f"(relatif), rendement conservé = **{100*ndx_ret_ratio:.1f} %** de BuyHold "
      f"(seuils de cette tâche : réduction MDD >{100*MDD_REDUCTION_THRESHOLD:.0f} %, "
      f"rendement conservé ≥{100*RET_KEEP_THRESHOLD:.0f} % — "
      f"{'ATTEINT' if ndx_mdd_red > MDD_REDUCTION_THRESHOLD and ndx_ret_ratio >= RET_KEEP_THRESHOLD else 'NON atteint (rendement conservé sous 80 %)'} "
      "sur NDX lui-même avec ces seuils précis — à garder en tête en lisant les "
      "3 indices ci-dessous).\n")

    for r in results:
        w(f"## 3.{results.index(r)+1}. {r['name']}\n")
        w(f"{r['rep']['n_obs']} séances, {r['rep']['start']:%d/%m/%Y} → "
          f"{r['rep']['end']:%d/%m/%Y}. OOS = {r['T_oos']} j "
          f"({r['dates_oos'][0]:%d/%m/%Y} → {r['dates_oos'][1]:%d/%m/%Y}).\n")
        w("| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | "
          "IC 95% Sharpe (bootstrap bloc) | Profit factor | Hit rate | Turnover/j | DSR (n=3) |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for v in VARIANTS:
            x = r["metr"][v]
            lo, hi = r["ci95"][v]
            w(f"| {v} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | "
              f"{x['calmar']:+.2f} | {x['ann_return_pct']:+.1f} % | "
              f"{x['max_drawdown_pct']:.1f} % | [{lo:+.2f}, {hi:+.2f}] | "
              f"{x['profit_factor']:.2f} | {100*x['hit_rate']:.1f} % | "
              f"{r['turnover'][v]:.3f} | {r['dsr'][v]['dsr']:.3f} |")
        w("")
        w(f"- Réduction relative du MDD (LogitL2+Overlay vs BuyHold) : "
          f"**{100*r['mdd_reduction']:+.1f} %** (seuil : >"
          f"{100*MDD_REDUCTION_THRESHOLD:.0f} %).")
        w(f"- Rendement annualisé conservé (LogitL2+Overlay / BuyHold) : "
          f"**{100*r['ret_ratio']:.1f} %** (seuil : ≥{100*RET_KEEP_THRESHOLD:.0f} %).")
        w(f"- Verdict {r['name']} : **{'SUCCÈS' if r['success'] else 'échec'}** "
          "du critère de généralisation sur cet indice.\n")

    w("## 4. Verdict cross-market\n")
    w("| Indice | ΔMDD relatif (Overlay vs BH) | Rdt conservé | Critère atteint |")
    w("|---|---|---|---|")
    for r in results:
        w(f"| {r['name']} | {fmt_pct(100*r['mdd_reduction'])} | "
          f"{r['ret_ratio']*100:.1f} % | {'OUI' if r['success'] else 'non'} |")
    w("")
    w(f"**{n_success}/3 indices** atteignent le critère de succès déclaré "
      f"(réduction MDD >{100*MDD_REDUCTION_THRESHOLD:.0f} % relatif **et** "
      f"rendement annualisé conservé ≥{100*RET_KEEP_THRESHOLD:.0f} % de "
      f"Buy & Hold). Seuil de succès de la tâche : ≥{N_SUCCESS_REQUIRED}/3.\n")
    if overall_success:
        w(f"**Verdict global : SUCCÈS.** Le pipeline LogitL2 + overlay (cap "
          f"{OVERLAY_CAP:.1f}×, coupe {OVERLAY_PCTL:.0f}e pctl) réduit "
          f"matériellement le drawdown sur {n_success}/3 indices externes "
          "sans sacrifier l'essentiel du rendement Buy & Hold — l'effet "
          "observé sur NDX (Étape D) **se généralise**, il n'est pas "
          "spécifique à ce seul marché.")
    else:
        w(f"**Verdict global : ÉCHEC du critère explicite.** Seuls "
          f"{n_success}/3 indices atteignent le seuil déclaré "
          f"(≥{N_SUCCESS_REQUIRED}/3 requis). Rapporté tel quel : le pipeline "
          "retenu sur NDX ne se généralise pas de façon fiable à ce niveau de "
          "seuil sur l'univers figé des 3 indices testés ici.")
    w("\nDiscipline anti data-snooping : univers figé (3 indices × 3 "
      "variantes = 9 tests), aucun paramètre (LogitL2, cap overlay, "
      "percentile de coupe) ré-optimisé sur ces marchés — ce sont exactement "
      "ceux déjà retenus et publiés sur NDX. DSR calculé séparément par "
      "indice (n_trials=3), jamais combiné statistiquement entre indices, "
      "conformément à la tâche.\n")

    Path(OUT).write_text("\n".join(lines))
    print("\n" + "\n".join(lines))
    print(f"\nRapport écrit : {OUT}")


if __name__ == "__main__":
    main()
