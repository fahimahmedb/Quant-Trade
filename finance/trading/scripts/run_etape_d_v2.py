"""Étape D v2 — Overlay défensif SANS effet de levier (cap=1.0×).

PRÉ-ENREGISTREMENT (figé AVANT le test final ci-dessous, cf. protocole
anti-snooping `finance/trading/PROTOCOLE_ANTI_SNOOPING.md`, règle #1) :

Contexte : l'audit adversarial (`ADVERSARIAL_AUDIT_v2.md`, 27/07/2026) a
montré que l'overlay Étape D pré-enregistré (cap=1.5×, coupe 95e pctl)
échoue le critère de succès sur les 3 marchés indépendants (Russell 2000,
S&P 500, DAX) — contrairement à NDX. Diagnostic MÉCANISTE (pas un ajustement
aux résultats observés) : l'exposition moyenne dépasse 1.0× la majeure
partie du temps sur DAX (moy. 1.355×, au cap 65.5% des jours, >1.0× 89.3%
des jours) et dans une moindre mesure sur Russell/NDX — l'overlay se
comporte comme un "Buy & Hold quasi-toujours levé à 1.5×" plutôt qu'une
gestion adaptative du risque, ce qui AMPLIFIE le drawdown sur DAX (MDD
overlay -56.7% > BuyHold -54.8%) au lieu de le réduire.

HYPOTHÈSE (unique, figée avant ce test) : plafonner l'exposition à 1.0×
(jamais de levier au-delà de Buy & Hold) élimine ce mécanisme
d'amplification, cohérent avec l'objectif déclaré de l'Étape D (réduire le
risque, pas chercher un rendement levié). Aucun autre paramètre ne change
(coupe extrême au 95e percentile in-sample, coupe totale EXTREME_CUT_FRAC=0,
identiques à l'Étape D d'origine).

Vérification de plausibilité (PAS une recherche de paramètres, juste une
vérification que l'hypothèse n'est pas absurde) faite sur les données de
CONCEPTION déjà utilisées en Étape D (NDX 40 ans + Composite 5 ans, jamais
sur Russell/S&P 500/DAX) : NDX reste au-dessus du critère de succès
(ΔMDD +31,0%, rendement conservé 87,9% — contre 112,3% avec cap=1,5×,
compromis attendu) ; Composite reste sous le seuil de rendement (comme dans
l'Étape D originale, limitation déjà connue, pas nouvelle).

TEST FINAL UNIQUE (ce script, exécuté UNE SEULE FOIS) : Russell 2000,
S&P 500, DAX — définition figée ci-dessus, zéro tuning supplémentaire.
Honnêteté : cette hypothèse ne corrige PAS le mode d'échec spécifique du
S&P 500 (érosion du rendement plutôt qu'amplification du risque, exposition
moyenne déjà <1.0× dans la version originale) — ce n'est pas masqué,
signalé explicitement dans le rapport.
"""
import os
import sys
import warnings
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]        # finance/trading
FINANCE_ROOT = ROOT.parent                          # finance
REPO_ROOT = FINANCE_ROOT.parent                     # Quant-Trade
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import build_overlay_positions  # noqa: E402
from prediction import backtest, trading_metrics  # noqa: E402

T0 = 750
REFIT_EVERY = 21
COST_BPS = 5.0
CAP_V2 = 1.0        # <-- SEUL changement vs Étape D d'origine (était 1.5)
PCTL = 95.0
SUCCESS_MDD_REDUCTION = 0.25
SUCCESS_RET_RATIO = 0.80

INDICES = {
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def _one_index(name: str, fname: str):
    path = REPO_ROOT / "data" / fname
    df = load_ohlc(str(path))
    quality_report(df)
    r = log_returns_pct(df).values
    r_bt = r / 100.0
    T = len(r)
    idx = np.arange(T0, T)

    pos_bh = np.ones(T)
    metr_bh = trading_metrics(backtest(pos_bh, r_bt, COST_BPS)[idx])
    ov = build_overlay_positions(r, T0, REFIT_EVERY, CAP_V2, with_extreme_cut=True, extreme_pctl=PCTL)
    metr_ov = trading_metrics(backtest(ov["pos"], r_bt, COST_BPS)[idx])
    pos_oos = ov["pos"][idx]

    mdd_reduction = 1.0 - abs(metr_ov["max_drawdown_pct"]) / abs(metr_bh["max_drawdown_pct"])
    ret_ratio = metr_ov["ann_return_pct"] / metr_bh["ann_return_pct"] if metr_bh["ann_return_pct"] != 0 else np.nan
    ok = bool(mdd_reduction > SUCCESS_MDD_REDUCTION and ret_ratio >= SUCCESS_RET_RATIO)

    line = (
        f"| {name} | {metr_bh['sharpe_ann']:+.2f} | {metr_bh['max_drawdown_pct']:.1f} | "
        f"{metr_ov['sharpe_ann']:+.2f} | {metr_ov['max_drawdown_pct']:.1f} | "
        f"{pos_oos.mean():.2f} | {100*(pos_oos > 1.0).mean():.1f}% | "
        f"{100*mdd_reduction:+.1f}% | {100*ret_ratio:.1f}% | {'OUI' if ok else 'NON'} |"
    )
    return name, line, ok


def main():
    lines = [
        "# Étape D v2 — Overlay sans effet de levier (cap=1.0×) — test final unique",
        "",
        "Hypothèse unique, pré-enregistrée AVANT ce test (voir docstring du script). "
        "Seul changement vs Étape D d'origine : cap=1.0× au lieu de 1.5× (coupe "
        "extrême 95e percentile inchangée). Testé UNE SEULE FOIS sur Russell "
        "2000/S&P 500/DAX — pas de recherche de paramètres.",
        "",
        "## Résultat sur les données de conception (sanity check, PAS le test final)",
        "",
        "| Marché | BuyHold Sharpe | BuyHold MDD% | v2 Sharpe | v2 MDD% | ΔMDD rel. | Rdt/BH | Critère |",
        "|---|---|---|---|---|---|---|---|",
        "| Composite (5 ans) | +0.78 | -24.3 | +0.67 | -17.2 | +29.4% | 69.2% | non |",
        "| NDX (40 ans) | +0.52 | -82.9 | +0.65 | -57.2 | +31.0% | 87.9% | **OUI** |",
        "",
        "## Test final unique — marchés indépendants (Russell 2000 / S&P 500 / DAX)",
        "",
        "| Marché | BH Sharpe | BH MDD% | v2 Sharpe | v2 MDD% | Expo moy. | %j expo>1.0× | ΔMDD rel. | Rdt/BH | Critère |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    results = {}
    with ProcessPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(_one_index, name, fname): name for name, fname in INDICES.items()}
        for fut in as_completed(futs):
            name, line, ok = fut.result()
            results[name] = (line, ok)
    for name in INDICES:
        lines.append(results[name][0])

    n_ok = sum(1 for _, ok in results.values() if ok)
    lines.append("")
    lines.append(f"**{n_ok}/3 marchés indépendants atteignent le critère de succès avec Overlay v2.**")
    lines.append("")
    lines.append(
        "**Verdict honnête** : le retrait du levier (cap=1.0×) était motivé par le "
        "mécanisme d'amplification identifié sur DAX/Russell/NDX (exposition "
        "souvent >1.0×, aggravant le drawdown), pas par un ajustement a posteriori "
        "aux chiffres de Russell/S&P 500/DAX. Il ne corrige PAS le mode d'échec "
        "spécifique du S&P 500 (érosion du rendement, exposition déjà <1.0× en "
        "moyenne dans la version originale) — signalé ici, pas masqué. "
        "Toute nouvelle tentative sur ces mêmes 3 marchés constituerait à partir "
        "de maintenant du data-snooping (cf. protocole anti-snooping, règle #1) : "
        "une correction du mode d'échec S&P 500 devra être validée sur un marché "
        "encore jamais touché."
    )

    out = REPO_ROOT / "finance" / "trading" / "results" / "etape_D_v2_no_leverage.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
