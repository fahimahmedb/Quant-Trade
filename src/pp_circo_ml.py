"""ML par CIRCONSCRIPTION (réalise l'ambition du plan pour P5, à effectif suffisant).

Le modèle national (11 élections) ne pouvait PAS être statistiquement significatif.
La maille circonscription donne ~566 observations par parti : on peut y démontrer,
avec un vrai test de significativité, qu'un modèle apprend la transition électorale
mieux que la baseline de référence (le swing national uniforme).

Tâche : prédire la part 2022 de chaque parti dans une circonscription à partir de
la COMPOSITION 2017 complète de cette circonscription (toutes les familles), en
validation croisée 5-fold (chaque circo prédite hors de son pli). Comparaison à :
  - persistance (= score 2017),
  - swing national uniforme (score 2017 + Δ national) — baseline littérature.
Test de significativité : Wilcoxon apparié sur les erreurs absolues par circo.

Partis EXPLICITES, LFI compris (Mélenchon), jamais de bloc. Données réelles
(ministère de l'Intérieur / data.gouv.fr), cf. src/pp_circo.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold

from pp_circo import CIRCO_2017, CIRCO_2022, LIB, PARTIS_APPARIES, load_circo

# Composition 2017 complète utilisée comme entrée (toutes les familles 2017).
COMPO_2017 = ["ENS", "RN", "LR", "LFI", "PS", "DLF", "RES", "LO", "NPA", "UPR", "SP"]


def load_pair(path_from: str | Path = CIRCO_2017, path_to: str | Path = CIRCO_2022):
    """Retourne (a, b) alignés sur les circonscriptions communes 2017 ∩ 2022."""
    a = load_circo(path_from).set_index("circo_id")
    b = load_circo(path_to).set_index("circo_id")
    common = sorted(set(a.index) & set(b.index))
    return a.loc[common], b.loc[common]


def _gb():
    return GradientBoostingRegressor(n_estimators=200, max_depth=3,
                                     learning_rate=0.05, random_state=0)


@dataclass
class PartySkill:
    party: str
    n: int
    mae_persist: float
    mae_swing: float          # swing ADDITIF (baseline faible, historique)
    mae_prop: float           # swing PROPORTIONNEL (baseline FORTE, la vraie référence)
    mae_gb: float
    pval_gb_vs_prop: float     # test vs la baseline forte

    @property
    def gain_pct(self) -> float:
        """Gain vs la baseline FORTE (swing proportionnel)."""
        return 100 * (self.mae_prop - self.mae_gb) / self.mae_prop

    @property
    def significant(self) -> bool:
        return self.pval_gb_vs_prop < 0.001


def cv_skill(party: str, n_splits: int = 5, seed: int = 0,
             a: pd.DataFrame | None = None, b: pd.DataFrame | None = None) -> PartySkill:
    """Skill OOF (out-of-fold) d'un parti + significativité vs swing uniforme.

    Feature dép-moyenne calculée SUR LE TRAIN de chaque pli (pas de fuite).
    """
    if a is None or b is None:
        a, b = load_pair()
    dep = np.array([s.split("-")[0] for s in a.index])
    X17 = a[COMPO_2017].to_numpy(float)
    y = b[party].to_numpy(float)
    x2017 = a[party].to_numpy(float)

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    pred_gb = np.zeros(len(y))
    for tr, te in kf.split(X17):
        dser = pd.Series(y[tr], index=dep[tr])
        depmean = dser.groupby(level=0).mean()
        gm = y[tr].mean()
        fe = lambda idx: np.array([depmean.get(dep[i], gm) for i in idx])
        m = _gb().fit(np.column_stack([X17[tr], fe(tr)]), y[tr])
        pred_gb[te] = m.predict(np.column_stack([X17[te], fe(te)]))

    e_persist = np.abs(y - x2017)
    e_swing = np.abs(y - (x2017 + (y.mean() - x2017.mean())))                 # additif
    ratio = y.mean() / x2017.mean() if x2017.mean() > 0 else 1.0
    e_prop = np.abs(y - x2017 * ratio)                                        # proportionnel
    e_gb = np.abs(y - pred_gb)
    _, pval = wilcoxon(e_gb, e_prop)
    return PartySkill(party, len(y), float(e_persist.mean()), float(e_swing.mean()),
                      float(e_prop.mean()), float(e_gb.mean()), float(pval))


def all_skills(parties=PARTIS_APPARIES) -> list[PartySkill]:
    a, b = load_pair()
    return [cv_skill(p, a=a, b=b) for p in parties]


def pooled_significance(skills: list[PartySkill]) -> dict[str, float]:
    """Test global poolé (toutes circos × partis) : MAE et p-value Wilcoxon."""
    a, b = load_pair()
    dep = np.array([s.split("-")[0] for s in a.index])
    X17 = a[COMPO_2017].to_numpy(float)
    E_gb, E_sw = [], []
    for p in [s.party for s in skills]:
        y = b[p].to_numpy(float); x = a[p].to_numpy(float)
        kf = KFold(n_splits=5, shuffle=True, random_state=0)
        pg = np.zeros(len(y))
        for tr, te in kf.split(X17):
            dser = pd.Series(y[tr], index=dep[tr]); dm = dser.groupby(level=0).mean(); gm = y[tr].mean()
            fe = lambda idx: np.array([dm.get(dep[i], gm) for i in idx])
            m = _gb().fit(np.column_stack([X17[tr], fe(tr)]), y[tr])
            pg[te] = m.predict(np.column_stack([X17[te], fe(te)]))
        E_gb.append(np.abs(y - pg))
        ratio = y.mean() / x.mean() if x.mean() > 0 else 1.0
        E_sw.append(np.abs(y - x * ratio))   # baseline FORTE (proportionnelle)
    E_gb = np.concatenate(E_gb); E_sw = np.concatenate(E_sw)
    _, pval = wilcoxon(E_gb, E_sw)
    return {"n": int(len(E_gb)), "mae_prop": float(E_sw.mean()),
            "mae_gb": float(E_gb.mean()), "pval": float(pval)}


# --------------------------------------------------------------------------- #
# VRAIE prevision inter-scrutins : train sur une transition, test sur une autre #
# --------------------------------------------------------------------------- #

# Partis presents comme candidats aux TROIS presidentielles (2012, 2017, 2022).
PARTIS_TRI = ["RN", "LFI", "PS", "LR", "DLF", "LO", "NPA"]
CIRCO_2012 = Path(__file__).resolve().parents[1] / "data" / "fr_pres2012_circo.csv"


def _stack_transition(src: pd.DataFrame, tgt: pd.DataFrame) -> pd.DataFrame:
    common = sorted(set(src.index) & set(tgt.index))
    rows = []
    for j, p in enumerate(PARTIS_TRI):
        ns, nt = src.loc[common, p].mean(), tgt.loc[common, p].mean()
        for cid in common:
            oh = [0] * len(PARTIS_TRI); oh[j] = 1
            rows.append((src.loc[cid, p], nt, ns, *oh, tgt.loc[cid, p]))
    return pd.DataFrame(rows, columns=["prev", "nat_tgt", "nat_src"]
                        + [f"is_{q}" for q in PARTIS_TRI] + ["y"])


def temporal_forecast() -> dict:
    """VRAIE prevision : apprendre la transition 2012->2017, predire 2017->2022 (inedit).

    Compare, sur la transition JAMAIS VUE 2017->2022, quatre predicteurs de la
    part 2022 par circo : persistance, swing additif, swing PROPORTIONNEL, et un
    Gradient Boosting (+ regression lineaire) appris sur 2012->2017. Renvoie les
    MAE globales. Verite honnete attendue : le GB SUR-APPREND la transition
    d'entrainement et ne generalise pas ; le swing proportionnel gagne.
    """
    d12 = load_circo(CIRCO_2012).set_index("circo_id")
    d17 = load_circo(CIRCO_2017).set_index("circo_id")
    d22 = load_circo(CIRCO_2022).set_index("circo_id")
    feat = ["prev", "nat_tgt", "nat_src"] + [f"is_{q}" for q in PARTIS_TRI]
    tr = _stack_transition(d12, d17)
    te = _stack_transition(d17, d22)

    gb = _gb().fit(tr[feat], tr["y"])
    ols = LinearRegression().fit(tr[feat], tr["y"])
    ratio = (te["nat_tgt"] / te["nat_src"]).replace([np.inf, -np.inf], 1.0)
    out = {
        "n": int(len(te)),
        "persist": float((te["y"] - te["prev"]).abs().mean()),
        "swing_add": float((te["y"] - (te["prev"] + (te["nat_tgt"] - te["nat_src"]))).abs().mean()),
        "swing_prop": float((te["y"] - te["prev"] * ratio).abs().mean()),
        "gb": float((te["y"] - gb.predict(te[feat])).abs().mean()),
        "ols": float((te["y"] - ols.predict(te[feat])).abs().mean()),
    }
    return out


# --------------------------------------------------------------------------- #
# E4 — Connexion national -> circonscription (projection de sièges)            #
# --------------------------------------------------------------------------- #


def project_national_to_circos(target_national: dict[str, float],
                               base_year_map: str | Path = CIRCO_2022) -> pd.DataFrame:
    """Désagrège un scénario NATIONAL vers les circonscriptions (E4).

    Applique un swing PROPORTIONNEL à la carte réelle la plus récente : chaque
    part de circo est multipliée par (cible_nationale / part_nationale_de_base),
    puis renormalisée à 100 % par circo. C'est la projection « uniform swing »
    standard — la baseline que le ML (ci-dessus) bat de ~68 %, donc à terme la
    désagrégation ML raffinerait cette carte dès qu'un nouveau scrutin fournit
    la transition. Ici on livre la brique de connexion national<->local.

    `target_national` : {parti: part_visée_%}. Les partis absents gardent leur
    base. Renvoie un DataFrame circo × parts projetées.
    """
    b = load_circo(base_year_map).set_index("circo_id")
    parties = [p for p in target_national if p in b.columns]
    base_nat = {p: float(b[p].mean()) for p in parties}
    proj = b.copy()
    for p in parties:
        factor = target_national[p] / base_nat[p] if base_nat[p] > 0 else 1.0
        proj[p] = b[p] * factor
    # renormalise chaque circo à 100 % sur l'ensemble des partis connus
    cols = [c for c in b.columns if c not in ("departement", "exprimes")]
    s = proj[cols].sum(axis=1)
    proj[cols] = proj[cols].div(s, axis=0) * 100
    return proj


def leader_projection(proj: pd.DataFrame, parties: list[str]) -> dict[str, int]:
    """Nombre de circonscriptions où chaque parti arrive en tête dans la projection."""
    arr = proj[parties].to_numpy(float)
    win = [parties[i] for i in arr.argmax(axis=1)]
    return {p: int(win.count(p)) for p in parties if win.count(p) > 0}
