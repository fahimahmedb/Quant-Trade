"""F17 — diagnostic de cause d'écart (Lot IA-1, docs/feature-plans/
ia-f10-f19.md §8, cible SYN-N). « F5 dit qu'il y a un écart récurrent. F17
propose pourquoi. »

Portée : les écarts SANS motif saisi. Un écart déjà motivé (casse, périmé,
offert...) a déjà sa réponse — F5 pose la même distinction (`LossBadge.
cumulative_value` de `ai_drift.classify_losses` est déjà « hors écarts
portant un motif »). F17 continue exactement cette distinction pour les
écarts qui n'en ont PAS, jamais pour proposer une seconde explication à un
écart déjà expliqué par le restaurateur lui-même.

Gate (§8) : « >= 6 comptages, et >= 3 écarts avec motif saisi ». Un seuil
d'ACTIVITÉ globale sur cet ingrédient (le champ motif est réellement
utilisé, donc les comptages sont fiables), pas un filtre sur les écarts
que les règles ci-dessous analysent — ceux-là restent, par construction,
les écarts SANS motif.

Quatre hypothèses, croisées indépendamment (jamais un choix arbitraire
entre plusieurs causes plausibles simultanées, TC-F17-05) :

1. **Affluence** — les écarts non expliqués se concentrent sur 1-2 jours
   de la semaine QUI SONT RÉELLEMENT les jours de plus fort volume de
   vente pour cet ingrédient (vérifié sur les ventes réelles, jamais
   supposé sur "vendredi/samedi = rush" — TC-F17-04 exige justement
   qu'aucune corrélation ne soit inventée sur des écarts sans structure).
2. **Zone** — d'autres ingrédients de la MÊME zone de stockage montrent
   eux aussi des écarts non expliqués, dans une proportion nettement
   supérieure aux autres zones : le problème n'est probablement pas cet
   ingrédient en particulier, mais sa zone (conservation, casse).
3. **Date** — les écarts non expliqués n'apparaissent qu'à partir d'une
   date précise (avant : rien ou presque ; après : régulièrement) —
   quelque chose a changé ce jour-là.
4. **Fiche technique (renvoi F5)** — si `ai_drift.detect_drift` a déjà une
   proposition pour cet ingrédient, F17 s'efface derrière elle plutôt que
   d'inventer une corrélation parallèle à la même donnée.

Formulation (AC-F17-3) : chaque hypothèse est une QUESTION, jamais une
affirmation — l'outil signale une corrélation, le chef sait l'expliquer.

Les seuils de concentration ci-dessous (part minimale, taille d'échantillon)
sont des décisions actées faute de valeur fournie par le document — mêmes
principes que les seuils réglables du Lot IA-0 (§8 des specs V2) : des
valeurs de départ raisonnées, pas des constantes validées par un pilote.
Contrairement aux seuils F5/F10-F16, ceux-ci ne sont PAS exposés comme
réglables : ce sont des règles de significativité statistique (taille
d'échantillon minimale, majorité claire), pas des choix métier comme "40%
d'écart d'import" — les rendre réglables inviterait à les baisser jusqu'à
obtenir une hypothèse, ce que TC-F17-04 interdit précisément.
"""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime

from sqlalchemy.orm import Session

from app import models
from app.services import ai_drift, settings_service
from app.templating import pluriel

MIN_COMPLETED_COUNTS = 6  # ia-f10-f19.md §8
MIN_MOTIVATED_VARIANCES = 3  # ia-f10-f19.md §8

# Règle "affluence"
WEEKDAY_MIN_UNEXPLAINED = 4  # échantillon minimal avant de tenter cette règle
WEEKDAY_CONCENTRATION_SHARE = 0.65  # part des 1-2 jours les + représentés
WEEKDAY_MAX_DAYS_FLAGGED = 2  # "1-2 jours", jamais une majorité de la semaine

# Règle "zone"
ZONE_MIN_PEERS = 3  # taille minimale de la zone pour qu'un "pattern" ait un sens
ZONE_AFFECTED_SHARE = 0.5  # part des ingrédients de la zone touchés
ZONE_RATIO_OVER_OTHERS = 2.0  # ... et nettement au-dessus des autres zones

# Règle "date"
DATE_MIN_SESSIONS_EACH_SIDE = 3
DATE_AFTER_SHARE = 0.6  # part des comptages "après" montrant un écart non expliqué

WEEKDAY_LABELS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


@dataclass
class DataGateResult:
    ok: bool
    message: str | None
    completed_counts: int = 0
    motivated_variances: int = 0


@dataclass
class Hypothesis:
    kind: str  # "affluence" | "zone" | "date" | "fiche_technique"
    question: str
    detail: str = ""


@dataclass
class DiagnosisResult:
    gate: DataGateResult
    ingredient_id: int | None = None
    hypotheses: list[Hypothesis] = field(default_factory=list)
    explanation: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f17_enabled


def _completed_lines(db: Session, ingredient_id: int) -> list[models.CountLine]:
    """Même requête que `ai_drift._completed_lines` (F5) : lignes de
    comptage terminées pour cet ingrédient, du plus ancien au plus récent."""
    return (
        db.query(models.CountLine)
        .join(models.CountSession)
        .filter(
            models.CountLine.ingredient_id == ingredient_id,
            models.CountSession.ended_at.isnot(None),
            models.CountLine.counted_quantity.isnot(None),
        )
        .order_by(models.CountSession.ended_at)
        .all()
    )


def _is_unexplained_loss(line: models.CountLine) -> bool:
    variance = line.variance or 0.0
    return variance > 0 and line.variance_reason is None


def data_gate(db: Session, ingredient_id: int) -> DataGateResult:
    """ia-f10-f19.md §8 : « >= 6 comptages, et >= 3 écarts avec motif
    saisi » — seuil d'activité, pas un filtre sur les écarts analysés
    (cf. docstring du module)."""
    lines = _completed_lines(db, ingredient_id)
    n = len(lines)
    motifs = sum(1 for l in lines if l.variance_reason is not None)
    if n < MIN_COMPLETED_COUNTS:
        return DataGateResult(
            ok=False, message=f"{n} comptage{pluriel(n)} sur {MIN_COMPLETED_COUNTS} nécessaires",
            completed_counts=n, motivated_variances=motifs,
        )
    if motifs < MIN_MOTIVATED_VARIANCES:
        return DataGateResult(
            ok=False,
            message=f"{motifs} écart{pluriel(motifs)} avec motif sur {MIN_MOTIVATED_VARIANCES} nécessaires",
            completed_counts=n, motivated_variances=motifs,
        )
    return DataGateResult(ok=True, message=None, completed_counts=n, motivated_variances=motifs)


def _weekday_sales_volume(db: Session, ingredient_id: int) -> dict[int, float]:
    """Volume de vente réel par jour de semaine, tous plats de la fiche
    technique de cet ingrédient confondus — la référence pour vérifier
    qu'un jour est RÉELLEMENT un jour de forte affluence, jamais supposé."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    dish_ids = [rl.dish_id for rl in recipe_lines]
    if not dish_ids:
        return {}
    volume: dict[int, float] = defaultdict(float)
    sales = db.query(models.SaleLine).filter(models.SaleLine.dish_id.in_(dish_ids)).all()
    for sale in sales:
        volume[sale.sale_date.weekday()] += sale.quantity_sold
    return dict(volume)


def _affluence_hypothesis(db: Session, ingredient: models.Ingredient, unexplained: list[models.CountLine]) -> Hypothesis | None:
    if len(unexplained) < WEEKDAY_MIN_UNEXPLAINED:
        return None

    par_jour: dict[int, int] = defaultdict(int)
    for line in unexplained:
        par_jour[line.count_session.ended_at.weekday()] += 1
    total = len(unexplained)

    jours_tries = sorted(par_jour, key=lambda wd: par_jour[wd], reverse=True)
    concentres: list[int] = []
    cumul = 0
    for wd in jours_tries[:WEEKDAY_MAX_DAYS_FLAGGED]:
        concentres.append(wd)
        cumul += par_jour[wd]
        if cumul / total >= WEEKDAY_CONCENTRATION_SHARE:
            break
    else:
        return None  # même les 2 jours les + représentés n'atteignent pas le seuil

    volumes = _weekday_sales_volume(db, ingredient.id)
    if not volumes:
        return None
    jours_forte_affluence = set(
        sorted(volumes, key=lambda wd: volumes[wd], reverse=True)[:len(concentres)]
    )
    if not set(concentres) <= jours_forte_affluence:
        return None  # concentration réelle, mais pas sur des jours réellement + vendeurs

    noms = " et ".join(WEEKDAY_LABELS[wd] for wd in sorted(concentres))
    return Hypothesis(
        kind="affluence",
        question=(
            f"Les écarts non expliqués sur {ingredient.name} se concentrent le {noms}, "
            "vos jours de plus forte vente pour cet ingrédient : portionnage sous le rush ?"
        ),
        detail=f"{cumul}/{total} écarts non expliqués sur ces jours.",
    )


def _zone_hypothesis(db: Session, ingredient: models.Ingredient) -> Hypothesis | None:
    peers = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.storage_zone == ingredient.storage_zone, models.Ingredient.is_active.is_(True))
        .all()
    )
    if len(peers) < ZONE_MIN_PEERS:
        return None

    def _affected(ing: models.Ingredient) -> bool:
        return any(_is_unexplained_loss(l) for l in _completed_lines(db, ing.id))

    zone_affected = sum(1 for p in peers if _affected(p))
    zone_share = zone_affected / len(peers)
    if zone_share < ZONE_AFFECTED_SHARE:
        return None

    others = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.storage_zone != ingredient.storage_zone, models.Ingredient.is_active.is_(True))
        .all()
    )
    if others:
        other_share = sum(1 for o in others if _affected(o)) / len(others)
        if other_share > 0 and zone_share < other_share * ZONE_RATIO_OVER_OTHERS:
            return None

    return Hypothesis(
        kind="zone",
        question=(
            f"{zone_affected}/{len(peers)} ingrédients de la zone {ingredient.storage_zone.label} "
            f"présentent eux aussi des écarts non expliqués : conservation ou casse dans "
            f"{ingredient.storage_zone.label} ?"
        ),
        detail=f"{zone_affected}/{len(peers)} ingrédients touchés dans la zone.",
    )


def _date_hypothesis(db: Session, ingredient: models.Ingredient, lines: list[models.CountLine]) -> Hypothesis | None:
    n = len(lines)
    flags = [_is_unexplained_loss(l) for l in lines]
    for split in range(DATE_MIN_SESSIONS_EACH_SIDE, n - DATE_MIN_SESSIONS_EACH_SIDE + 1):
        before, after = flags[:split], flags[split:]
        if any(before):
            continue
        if sum(after) / len(after) >= DATE_AFTER_SHARE:
            split_date = lines[split].count_session.ended_at
            return Hypothesis(
                kind="date",
                question=(
                    f"Les écarts non expliqués sur {ingredient.name} apparaissent après le "
                    f"{split_date:%d/%m/%Y} : quelque chose a changé à cette date — nouveau "
                    "fournisseur, nouvelle équipe, recette modifiée ?"
                ),
                detail=f"{sum(after)}/{len(after)} comptages non expliqués depuis cette date.",
            )
    return None


def _fiche_technique_hypothesis(db: Session, ingredient_id: int) -> Hypothesis | None:
    drift = ai_drift.detect_drift(db, ingredient_id)
    if drift.proposal is None:
        return None
    dish = db.get(models.Dish, drift.proposal.dish_id)
    return Hypothesis(
        kind="fiche_technique",
        question=(
            f"Cet écart évolue avec les ventes de {dish.name} : la fiche technique "
            "sous-estime-t-elle la quantité réellement utilisée ?"
        ),
        detail=f"Voir F5 : proposition sur {dish.name} (corrélation {drift.proposal.correlation:.2f}).",
    )


def diagnose(db: Session, ingredient_id: int) -> DiagnosisResult:
    """ia-f10-f19.md §8 (SYN-N). Renvoie TOUTES les hypothèses dont les
    signaux sont réunis (TC-F17-05 : jamais un choix arbitraire entre
    plusieurs causes plausibles), chacune sous forme de question."""
    if not _feature_enabled(db):
        return DiagnosisResult(
            gate=DataGateResult(ok=False, message="Fonctionnalité F17 désactivée (feature flag éteint)."),
        )

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return DiagnosisResult(gate=DataGateResult(ok=False, message="Ingrédient introuvable."))

    gate = data_gate(db, ingredient_id)
    if not gate.ok:
        return DiagnosisResult(gate=gate, ingredient_id=ingredient_id, explanation=gate.message or "")

    lines = _completed_lines(db, ingredient_id)
    unexplained = [l for l in lines if _is_unexplained_loss(l)]

    hypotheses: list[Hypothesis] = []
    for candidate in (
        _affluence_hypothesis(db, ingredient, unexplained),
        _zone_hypothesis(db, ingredient),
        _date_hypothesis(db, ingredient, lines),
        _fiche_technique_hypothesis(db, ingredient_id),
    ):
        if candidate is not None:
            hypotheses.append(candidate)

    explanation = (
        f"{len(hypotheses)} hypothèse{pluriel(len(hypotheses))} proposée{pluriel(len(hypotheses))}."
        if hypotheses else "Aucune corrélation nette entre les écarts non expliqués et un jour, une zone, "
        "une date ou un plat : pas d'hypothèse à proposer."
    )
    return DiagnosisResult(gate=gate, ingredient_id=ingredient_id, hypotheses=hypotheses, explanation=explanation)
