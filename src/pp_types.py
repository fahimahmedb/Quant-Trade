"""Contrat d'interfaces du module « prédiction politique » (pp = political prediction).

CE FICHIER EST LE POINT DE RENDEZ-VOUS DE TOUTES LES BRIQUES (fondamentaux,
marchés, NLP, fusion, backtest). Il est figé AVANT le développement parallèle :
chaque source implémente le protocole `Source` et renvoie un `SourceSignal`
homogène, ce qui permet à la fusion bayésienne de les combiner sans connaître
leur mécanique interne.

Périmètre : élections françaises à deux tours (présidentielle). La grandeur
centrale, commune à toutes les sources et scorée par le backtest, est la
**part du candidat de référence au 2nd tour** (`r2_share`, dans [0, 1]), d'où
l'on déduit la probabilité de victoire P(r2_share > 0.5).

Choix du « candidat de référence » : le finaliste de continuité / sortant
(camp au pouvoir ou son héritier). L'axe scoré est donc « continuité vs
challenger anti-système ». Voir data/fr_presidentielles.json.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, Sequence, runtime_checkable

# --------------------------------------------------------------------------- #
# Description d'une élection (contexte connu AVANT le résultat)                #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Candidate:
    """Un candidat au 1er tour."""

    id: str          # identifiant stable, ex. "macron_2022"
    name: str
    camp: str        # "gauche" | "centre" | "droite" | "RN" | "gaulliste" | ...
    incumbent: bool  # représente-t-il le camp au pouvoir sortant ?


@dataclass(frozen=True)
class ElectionContext:
    """Tout ce qui est connu à la date de prévision (pas le résultat)."""

    election_id: str            # "FR_pres_2022"
    year: int
    reference_id: str           # candidat de référence (continuité/sortant)
    candidates: tuple[Candidate, ...]
    incumbent_running: bool     # le camp au pouvoir concourt-il réellement ?
    features: Mapping[str, float] = field(default_factory=dict)
    country: str = "FR"
    kind: str = "presidentielle"
    rounds: int = 2

    def reference(self) -> Candidate:
        for c in self.candidates:
            if c.id == self.reference_id:
                return c
        raise KeyError(f"reference_id {self.reference_id!r} absent de {self.election_id}")


@dataclass(frozen=True)
class ElectionResult:
    """Vérité terrain (utilisée en entraînement OOS et pour scorer)."""

    election_id: str
    r1_shares: Mapping[str, float]        # candidate_id -> part 1er tour (0..1)
    r2_finalists: tuple[str, str]
    r2_shares: Mapping[str, float]        # candidate_id -> part 2nd tour (0..1)
    winner_id: str

    def r2_reference_share(self, reference_id: str) -> float:
        """Part 2nd tour du candidat de référence, ou son report implicite.

        Si la référence n'est pas finaliste (ex. camp sortant éliminé au 1er
        tour), on renvoie NaN : l'élection reste utilisable pour le 1er tour
        mais est neutralisée dans le score 2nd tour côté référence.
        """
        return float(self.r2_shares.get(reference_id, float("nan")))


@dataclass(frozen=True)
class TrainingExample:
    """Paire (contexte, résultat) : la matière d'entraînement d'une source."""

    context: ElectionContext
    result: ElectionResult


# --------------------------------------------------------------------------- #
# Sortie homogène d'une source                                                 #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SourceSignal:
    """Ce que TOUTE source (fondamentaux, marchés, NLP) renvoie.

    Le cœur fusionnable est (r2_share_mean, r2_share_sd) : une estimation
    gaussienne de la part 2nd tour de la référence. `r2_share_sd` encode la
    confiance : plus il est grand, moins la source pèse dans la fusion
    (pondération par précision = 1/variance).

    `available` = False signale que la source n'a pas de donnée pour cette
    élection (ex. marchés inexistants en 1974) ; la fusion l'ignore alors.
    """

    source: str                     # "fundamentals" | "markets" | "nlp"
    election_id: str
    r2_share_mean: float            # E[part réf. au 2nd tour], dans [0, 1]
    r2_share_sd: float              # écart-type (incertitude), > 0
    available: bool = True
    r1_shares: Mapping[str, float] | None = None   # optionnel : parts 1er tour
    meta: Mapping[str, float] = field(default_factory=dict)

    def precision(self) -> float:
        """Précision = 1/variance (0 si indisponible ou dégénérée)."""
        if not self.available or self.r2_share_sd <= 0:
            return 0.0
        return 1.0 / (self.r2_share_sd * self.r2_share_sd)


@dataclass(frozen=True)
class Posterior:
    """Résultat de la fusion multi-source pour une élection."""

    election_id: str
    reference_id: str
    r2_share_mean: float
    r2_share_sd: float
    p_reference_wins: float                         # P(r2_share > 0.5)
    r1_shares: Mapping[str, float] | None = None
    contributions: Mapping[str, float] = field(default_factory=dict)  # source -> poids


# --------------------------------------------------------------------------- #
# Protocole que chaque brique doit implémenter                                 #
# --------------------------------------------------------------------------- #


@runtime_checkable
class Source(Protocol):
    """Interface commune (style scikit-learn : fit puis predict).

    Discipline anti-data-snooping : le backtest n'appelle `fit` qu'avec des
    élections STRICTEMENT antérieures à celle testée. Une source qui ne
    s'entraîne pas (ex. lecture directe d'un prix de marché) implémente `fit`
    en no-op renvoyant `self`.
    """

    name: str

    def fit(self, history: Sequence[TrainingExample]) -> "Source":
        ...

    def predict(self, ctx: ElectionContext) -> SourceSignal:
        ...


# Bornes de sécurité communes (part de vote plausible d'un finaliste).
SHARE_FLOOR = 0.15
SHARE_CEIL = 0.85


def clamp_share(x: float, lo: float = SHARE_FLOOR, hi: float = SHARE_CEIL) -> float:
    """Borne une part 2nd tour dans un intervalle plausible (anti-aberration)."""
    if x != x:  # NaN
        return 0.5
    return max(lo, min(hi, x))
