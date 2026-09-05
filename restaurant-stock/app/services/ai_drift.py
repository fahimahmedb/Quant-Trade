"""F5 — détection de dérive de fiche technique et classification des écarts
récurrents (Lot IA-0, docs/IA scope.md §1.3-1.6 pour les jeux SYN, extension
F10-F19 pour le contexte des principes généraux).

Deux capacités indépendantes, chacune gatée par les mêmes données
(≥ 4 comptages complets pour l'ingrédient concerné — docs/IA scope.md §1.6,
message exact repris de SYN-E) et par le même feature flag
(`Settings.feature_f5_enabled`, éteint par défaut : cf. docs/IA scope.md,
« toutes derrière un feature flag éteint ») :

1. `detect_drift` — un plat représentant ≥ 50% de la consommation théorique
   de l'ingrédient, dont le volume de vente par période corrèle (≥ 0,8) à
   l'écart constaté à chaque comptage, indique une fiche technique sous-
   évaluée : la pente de la régression donne la quantité corrigée proposée.
2. `classify_losses` — badge « perte récurrente » (≥ 3 pertes consécutives
   de magnitude comparable) ou « inhabituel » (une perte isolée très
   supérieure à l'historique de l'ingrédient), jamais les deux à la fois.

Explicabilité (principe des specs V2, rappelé en tête de l'extension
F10-F19) : aucune régression ni corrélation n'est cachée derrière une
bibliothèque — les deux tiennent en une douzaine de lignes ci-dessous,
lisibles et auditables sans dépendance externe (le projet n'a ni numpy ni
pandas, et ne devrait pas en avoir besoin ici : ce n'est pas de l'IA
prédictive, cf. app/services/ordering.py).
"""
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service
from app.templating import pluriel

MIN_COMPLETED_COUNTS = 4
DRIFT_SHARE_THRESHOLD = 0.5
DRIFT_CORRELATION_THRESHOLD = 0.8
RECURRING_MIN_STREAK = 3
RECURRING_MAGNITUDE_RATIO = 3.0  # écart max/min toléré dans une série "récurrente"
ANOMALY_RATIO = 5.0  # perte >= 5x la moyenne des pertes précédentes -> isolée
ANOMALY_MIN_PCT = 15.0  # à défaut d'historique de pertes, seuil relatif pour ne pas alerter sur du bruit


@dataclass
class DataGateResult:
    ok: bool
    message: str | None
    completed_counts: int


@dataclass
class DriftProposal:
    ingredient_id: int
    dish_id: int
    declared_quantity: float
    proposed_quantity: float
    correlation: float
    dish_share: float


@dataclass
class DriftResult:
    gate: DataGateResult
    proposal: DriftProposal | None
    explanation: str


@dataclass
class LossBadge:
    ingredient_id: int
    kind: str  # "perte_recurrente" | "inhabituel"
    cumulative_value: float | None = None
    streak_length: int | None = None
    session_id: int | None = None


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f5_enabled


def _disabled_gate() -> DataGateResult:
    return DataGateResult(ok=False, message="Fonctionnalité F5 désactivée (feature flag éteint).", completed_counts=0)


def data_gate(db: Session, ingredient_id: int) -> DataGateResult:
    """≥ 4 comptages complets pour CET ingrédient (docs/IA scope.md §1.6).
    Compté sur les lignes de comptage, pas les sessions du restaurant : un
    ingrédient ajouté après coup peut avoir moins d'historique que le reste."""
    n = (
        db.query(models.CountLine)
        .join(models.CountSession)
        .filter(
            models.CountLine.ingredient_id == ingredient_id,
            models.CountSession.ended_at.isnot(None),
            models.CountLine.counted_quantity.isnot(None),
        )
        .count()
    )
    if n >= MIN_COMPLETED_COUNTS:
        return DataGateResult(ok=True, message=None, completed_counts=n)
    return DataGateResult(
        ok=False,
        message=f"{n} comptage{pluriel(n)} sur {MIN_COMPLETED_COUNTS} nécessaires",
        completed_counts=n,
    )


def _completed_lines(db: Session, ingredient_id: int) -> list[models.CountLine]:
    """Lignes de comptage terminées pour cet ingrédient, du plus ancien au
    plus récent (ordre chronologique de clôture de session)."""
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


def _dish_qty_sold_between(db: Session, dish_id: int, start: datetime | None, end: datetime) -> float:
    query = db.query(models.SaleLine).filter(
        models.SaleLine.dish_id == dish_id, models.SaleLine.sale_date <= end,
    )
    if start is not None:
        query = query.filter(models.SaleLine.sale_date > start)
    return sum(line.quantity_sold for line in query.all())


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    std_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    if std_x == 0 or std_y == 0:
        return None
    return cov / (std_x * std_y)


def _slope(xs: list[float], ys: list[float]) -> float:
    """Pente de la régression linéaire simple y = a*x + b (méthode des
    moindres carrés) : `a`, le supplément de perte par unité vendue."""
    n = len(xs)
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    den = sum((x - mean_x) ** 2 for x in xs)
    if den == 0:
        return 0.0
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    return num / den


def detect_drift(db: Session, ingredient_id: int) -> DriftResult:
    """docs/IA scope.md §1.3/1.4 (SYN-B/C). Renvoie une proposition de
    grammage corrigé si UN plat représente >= 50% de la consommation
    théorique de l'ingrédient ET que son volume de vente par période
    corrèle (>= 0,8) à l'écart constaté à chaque comptage. Sinon, explique
    pourquoi (gate non atteint, ou perte réelle non attribuable à un plat)."""
    if not _feature_enabled(db):
        return DriftResult(gate=_disabled_gate(), proposal=None, explanation=_disabled_gate().message)

    gate = data_gate(db, ingredient_id)
    if not gate.ok:
        return DriftResult(gate=gate, proposal=None, explanation=f"Règle v1 appliquée : {gate.message}.")

    lines = _completed_lines(db, ingredient_id)
    periods: list[tuple[datetime | None, datetime]] = []
    prev_end = None
    for line in lines:
        periods.append((prev_end, line.count_session.ended_at))
        prev_end = line.count_session.ended_at
    variances = [line.variance or 0.0 for line in lines]

    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    if not recipe_lines:
        return DriftResult(gate=gate, proposal=None, explanation="Aucune fiche technique n'utilise cet ingrédient.")

    per_dish_total = {
        rl.dish_id: rl.quantity * _dish_qty_sold_between(db, rl.dish_id, None, periods[-1][1])
        for rl in recipe_lines
    }
    total_theoretical = sum(per_dish_total.values())

    for rl in recipe_lines:
        share = per_dish_total[rl.dish_id] / total_theoretical if total_theoretical else 0.0
        if share < DRIFT_SHARE_THRESHOLD:
            continue
        volumes = [_dish_qty_sold_between(db, rl.dish_id, p_start, p_end) for p_start, p_end in periods]
        correlation = _pearson(volumes, variances)
        if correlation is None or correlation < DRIFT_CORRELATION_THRESHOLD:
            continue
        slope = _slope(volumes, variances)
        proposal = DriftProposal(
            ingredient_id=ingredient_id, dish_id=rl.dish_id,
            declared_quantity=rl.quantity, proposed_quantity=rl.quantity + slope,
            correlation=correlation, dish_share=share,
        )
        return DriftResult(gate=gate, proposal=proposal, explanation="Dérive de grammage détectée.")

    return DriftResult(
        gate=gate, proposal=None,
        explanation=(
            "Un écart existe mais aucun plat ne représente au moins 50% de la "
            "consommation de cet ingrédient avec une corrélation suffisante à "
            "l'écart constaté : impossible de l'attribuer à une fiche technique précise."
        ),
    )


def classify_losses(db: Session, ingredient_id: int) -> LossBadge | None:
    """docs/IA scope.md §1.5 (SYN-D). `None` = ni "perte récurrente" ni
    "inhabituel" (y compris si le gate de données n'est pas atteint)."""
    if not _feature_enabled(db):
        return None
    if not data_gate(db, ingredient_id).ok:
        return None

    lines = _completed_lines(db, ingredient_id)
    variances = [(line.count_session_id, line.variance or 0.0, line.variance_value or 0.0) for line in lines]

    streak: list[tuple[int, float, float]] = []
    for item in reversed(variances):
        if item[1] > 0:
            streak.append(item)
        else:
            break
    if len(streak) >= RECURRING_MIN_STREAK:
        magnitudes = [abs(v) for _, v, _ in streak]
        if max(magnitudes) <= min(magnitudes) * RECURRING_MAGNITUDE_RATIO:
            return LossBadge(
                ingredient_id=ingredient_id, kind="perte_recurrente",
                cumulative_value=sum(val for _, _, val in streak),
                streak_length=len(streak),
            )

    last_session_id, last_variance, last_value = variances[-1]
    if last_variance > 0:
        prior_losses = [v for _, v, _ in variances[:-1] if v > 0]
        if prior_losses:
            baseline = sum(prior_losses) / len(prior_losses)
            is_anomaly = last_variance >= baseline * ANOMALY_RATIO
        else:
            is_anomaly = (lines[-1].variance_pct or 0.0) >= ANOMALY_MIN_PCT
        if is_anomaly:
            return LossBadge(
                ingredient_id=ingredient_id, kind="inhabituel",
                cumulative_value=last_value, session_id=last_session_id,
            )

    return None
