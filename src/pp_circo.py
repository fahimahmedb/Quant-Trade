"""Etape 4 — analyse par CIRCONSCRIPTION, niveau PARTI (LFI explicite, pas de bloc).

Donnees REELLES : presidentielle 2022, 1er tour, parts par circonscription
legislative et par parti (data/fr_pres2022_circo.csv, source ministere de
l'Interieur via data.gouv.fr). L'agregat national reconstitue = resultats
officiels au centieme (validation du parsing).

But (cf. demande utilisateur) : mesurer si la maille circonscription APPORTE au
modele, et le faire au niveau PARTI (Melenchon = LFI, distinct de PS/EELV — pas
noye dans un bloc « NFP/UG » comme dans les nuances legislatives officielles).

Methode sourcee : donnees compositionnelles multipartis (Hanretty 2021, regression
de Dirichlet ; procedure correction-combinaison au niveau circonscription). Ici on
teste la brique la plus simple et la plus robuste : la structure SPATIALE
(departementale) bat-elle la moyenne nationale plate pour predire la part locale ?
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CIRCO_2022 = ROOT / "data" / "fr_pres2022_circo.csv"
CIRCO_2017 = ROOT / "data" / "fr_pres2017_circo.csv"

# Partis mappables 2017 <-> 2022 (meme famille, candidat different possible) :
# LFI Melenchon/Melenchon, RN Le Pen/Le Pen, ENS Macron/Macron, LR Fillon/Pecresse,
# PS Hamon/Hidalgo, DLF/RES/LO/NPA memes candidats. EELV/REC/PCF non appariables.
PARTIS_APPARIES = ["LFI", "RN", "ENS", "LR", "PS", "DLF", "RES", "LO", "NPA"]

# Partis, du plus grand au plus petit (national 2022).
PARTIS = ["ENS", "RN", "LFI", "REC", "LR", "EELV", "RES", "PCF", "DLF", "PS", "NPA", "LO"]
LIB = {
    "ENS": "Macron (Ensemble)", "RN": "Le Pen (RN)", "LFI": "Mélenchon (LFI)",
    "REC": "Zemmour (Reconquête)", "LR": "Pécresse (LR)", "EELV": "Jadot (Écologistes)",
    "RES": "Lassalle (Résistons)", "PCF": "Roussel (PCF)", "DLF": "Dupont-Aignan (DLF)",
    "PS": "Hidalgo (PS)", "NPA": "Poutou (NPA)", "LO": "Arthaud (LO)",
}


def load_circo(path: str | Path = CIRCO_2022) -> pd.DataFrame:
    """577 circonscriptions × parts de vote (%) par parti. Données réelles."""
    return pd.read_csv(path, comment="#")


def national_shares(df: pd.DataFrame) -> dict[str, float]:
    """Part nationale reconstituée (pondérée par les exprimés) = contrôle parsing."""
    w = df["exprimes"].to_numpy(float)
    return {p: float((df[p].to_numpy(float) * w).sum() / w.sum()) for p in PARTIS}


def leader_counts(df: pd.DataFrame) -> dict[str, int]:
    """Nombre de circonscriptions où chaque parti arrive EN TÊTE (1er tour)."""
    arr = df[PARTIS].to_numpy(float)
    winners = [PARTIS[i] for i in arr.argmax(axis=1)]
    return {p: int(winners.count(p)) for p in PARTIS if winners.count(p) > 0}


def top2_counts(df: pd.DataFrame) -> dict[frozenset, int]:
    """Duos de tête (les 2 premiers) par circonscription."""
    arr = df[PARTIS].to_numpy(float)
    out: dict[frozenset, int] = {}
    for row in arr:
        top2 = frozenset(PARTIS[i] for i in row.argsort()[::-1][:2])
        out[top2] = out.get(top2, 0) + 1
    return out


def dispersion(df: pd.DataFrame, party: str) -> dict[str, float]:
    """Étendue spatiale d'un parti (min/max/écart-type sur les circos)."""
    v = df[party].to_numpy(float)
    return {"mean": float(v.mean()), "min": float(v.min()),
            "max": float(v.max()), "std": float(v.std())}


def swing_skill(party: str,
                path_from: str | Path = CIRCO_2017,
                path_to: str | Path = CIRCO_2022) -> dict[str, float]:
    """Test de skill TEMPOREL par circonscription (downscaling d'un tour à l'autre).

    Étant donné le résultat NATIONAL de l'élection cible, comment le distribuer
    aux circonscriptions ? On compare trois prédicteurs de la part locale cible,
    par leave-one-out sur les circos communes :
      - `persist`  : part de l'élection source (aucun swing).
      - `swing`    : swing NATIONAL UNIFORME (part source + Δ national) — la
                     baseline de référence de la littérature (Hanretty 2021).
      - `regress`  : régression 1D locale (cible ~ source), LOO — capture les
                     swings NON uniformes (regression to the mean, dynamiques
                     géographiques propres à un parti).

    Renvoie les MAE (points de %) ; `regress < swing` => la maille apporte une
    skill de prévision réelle, au-delà du swing uniforme.
    """
    a = load_circo(path_from).set_index("circo_id")
    b = load_circo(path_to).set_index("circo_id")
    common = a.index.intersection(b.index)
    x = a.loc[common, party].to_numpy(float)
    y = b.loc[common, party].to_numpy(float)
    n = len(x)

    persist = float(np.mean(np.abs(y - x)))
    swing = float(np.mean(np.abs(y - (x + (y.mean() - x.mean())))))

    sx, sy, sxx, sxy = x.sum(), y.sum(), (x * x).sum(), (x * y).sum()
    ae = []
    for i in range(n):
        n1, sx1, sy1 = n - 1, sx - x[i], sy - y[i]
        sxx1, sxy1 = sxx - x[i] ** 2, sxy - x[i] * y[i]
        den = n1 * sxx1 - sx1 ** 2
        b1 = (n1 * sxy1 - sx1 * sy1) / den if den != 0 else 0.0
        b0 = (sy1 - b1 * sx1) / n1
        ae.append(abs(y[i] - (b0 + b1 * x[i])))
    regress = float(np.mean(ae))
    return {"n": n, "persist": persist, "swing": swing, "regress": regress}


def dept_loo_mae(df: pd.DataFrame, party: str) -> tuple[float, float]:
    """Test OOS : prédire la part locale d'un parti.

    Renvoie (MAE_baseline_national, MAE_modele_departemental).
    - baseline : moyenne NATIONALE plate (le chiffre du modèle national).
    - modèle : moyenne du DÉPARTEMENT en leave-one-out (les AUTRES circos du
      département), i.e. la structure spatiale. Si le modèle départemental fait
      moins d'erreur, la maille circonscription porte un signal réel.
    """
    y = df[party].to_numpy(float)
    nat = y.mean()
    ae_nat, ae_dep = [], []
    for dep, sub in df.groupby("departement"):
        vals = sub[party].to_numpy(float)
        s, n = vals.sum(), len(vals)
        for yi in vals:
            ae_nat.append(abs(yi - nat))
            loo = (s - yi) / (n - 1) if n > 1 else nat   # moyenne des autres circos du dép
            ae_dep.append(abs(yi - loo))
    return float(np.mean(ae_nat)), float(np.mean(ae_dep))
