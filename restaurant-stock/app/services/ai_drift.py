"""F5 — détection de dérive de fiche technique et classification des écarts
récurrents (Lot IA-0, docs/feature-plans/ia-f5-f9.md §1.3-1.6 pour les jeux SYN, extension
F10-F19 pour le contexte des principes généraux).

Deux capacités indépendantes, chacune gatée par les mêmes données
(≥ 4 comptages complets pour l'ingrédient concerné — docs/feature-plans/ia-f5-f9.md §1.6,
message exact repris de SYN-E) et par le même feature flag
(`Settings.feature_f5_enabled`, éteint par défaut : cf. docs/feature-plans/ia-f5-f9.md,
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
import statistics
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service
from app.templating import pluriel

MIN_COMPLETED_COUNTS = 4
MIN_WEEKS_OF_SALES = 4.0  # specs-v2 §4 F5 : « >= 4 comptages validés ET >= 4 semaines de ventes »
DRIFT_SHARE_THRESHOLD = 0.5
DRIFT_CORRELATION_THRESHOLD = 0.8
RECURRING_MIN_STREAK = 3  # specs-v2 §4 F5 : « sur 3 comptages consécutifs »
ANOMALY_RATIO = 3.0  # specs-v2 §4 F5 : « supérieur à 3 fois la MÉDIANE des écarts historiques »
# Garde-fou hors spec, pour le cas dégénéré où la médiane historique est nulle
# (tous les comptages précédents conformes) : « 3 x 0 » ferait alerter sur le
# moindre gramme de bruit. Cf. SYN-D, scénario anomalie.
ANOMALY_MIN_PCT = 15.0


@dataclass
class DataGateResult:
    ok: bool
    message: str | None
    completed_counts: int
    weeks_of_sales: float = 0.0


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
    cumulative_value: float | None = None  # cumul INEXPLIQUÉ (hors écarts portant un motif)
    cumulative_value_total: float | None = None  # cumul total, motifs compris (AC-F5-5)
    streak_length: int | None = None
    session_id: int | None = None
    explanation: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f5_enabled


def _disabled_gate() -> DataGateResult:
    return DataGateResult(ok=False, message="Fonctionnalité F5 désactivée (feature flag éteint).", completed_counts=0)


def _weeks_of_sales(db: Session, ingredient_id: int) -> float:
    """Étendue de l'historique de ventes des plats qui utilisent cet
    ingrédient, en semaines. Mesurée sur les VENTES (pas les comptages) :
    c'est bien « X semaines de ventes » que specs-v2 §4 exige, et un
    ingrédient peut avoir été compté plusieurs fois sans qu'un plat qui
    l'utilise ait jamais été vendu."""
    dish_ids = [
        rl.dish_id for rl in db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    ]
    if not dish_ids:
        return 0.0
    dates = [
        s.sale_date for s in db.query(models.SaleLine).filter(models.SaleLine.dish_id.in_(dish_ids)).all()
    ]
    if not dates:
        return 0.0
    return ((max(dates).date() - min(dates).date()).days + 1) / 7.0


def data_gate(db: Session, ingredient_id: int) -> DataGateResult:
    """specs-v2-ia-plan-test.md §4 (F5) : « >= 4 comptages validés et >= 4
    semaines de ventes ». Les comptages sont comptés sur les LIGNES de
    comptage, pas les sessions du restaurant : un ingrédient ajouté après
    coup a moins d'historique que le reste (TC-F5-07)."""
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
    weeks = _weeks_of_sales(db, ingredient_id)
    if n < MIN_COMPLETED_COUNTS:
        return DataGateResult(
            ok=False,
            message=f"{n} comptage{pluriel(n)} sur {MIN_COMPLETED_COUNTS} nécessaires",
            completed_counts=n, weeks_of_sales=weeks,
        )
    if weeks < MIN_WEEKS_OF_SALES:
        return DataGateResult(
            ok=False,
            message=f"{weeks:.1f} semaines de ventes sur {MIN_WEEKS_OF_SALES:.0f} nécessaires",
            completed_counts=n, weeks_of_sales=weeks,
        )
    return DataGateResult(ok=True, message=None, completed_counts=n, weeks_of_sales=weeks)


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
    """docs/feature-plans/ia-f5-f9.md §1.3/1.4 (SYN-B/C). Renvoie une proposition de
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


def _theoretical_consumption_between(
    db: Session, ingredient_id: int, start: datetime | None, end: datetime,
) -> float:
    """Consommation théorique de l'ingrédient sur ]start, end] : Σ sur les
    fiches techniques de (grammage × quantités vendues). C'est la référence
    du seuil « 5 % de sa consommation théorique de la période » de specs-v2
    §4 (F5) — pas le stock théorique, qui mélange réceptions et
    ajustements sans rapport avec ce qui a réellement été cuisiné."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    return sum(rl.quantity * _dish_qty_sold_between(db, rl.dish_id, start, end) for rl in recipe_lines)


@dataclass
class _LossObservation:
    session_id: int
    variance: float  # > 0 = perte
    value: float  # écart valorisé en €
    pct_of_consumption: float
    explained: bool  # un motif (casse, périmé, offert…) a été saisi au comptage
    significant: bool


def _loss_observations(db: Session, ingredient_id: int) -> list[_LossObservation]:
    """Une observation par comptage terminé, du plus ancien au plus récent.

    `significant` applique le seuil de specs-v2 §4 (F5) : l'écart valorisé
    dépasse `loss_alert_pct` % de la consommation théorique de la période OU
    `loss_alert_eur` €. Les deux bornes sont réglables (§8 du document : ce
    sont « des valeurs de départ raisonnées, pas des constantes validées »).
    Le pourcentage se calcule en quantité, ce qui revient au même qu'en
    valeur : le coût unitaire multiplie identiquement les deux termes.
    """
    settings = settings_service.get_settings(db)
    lines = _completed_lines(db, ingredient_id)
    out: list[_LossObservation] = []
    prev_end: datetime | None = None
    for line in lines:
        end = line.count_session.ended_at
        consumption = _theoretical_consumption_between(db, ingredient_id, prev_end, end)
        prev_end = end
        variance = line.variance or 0.0
        value = line.variance_value or 0.0
        pct = (variance / consumption * 100.0) if consumption > 0 else 0.0
        significant = variance > 0 and (
            value >= settings.loss_alert_eur or pct >= settings.loss_alert_pct
        )
        out.append(_LossObservation(
            session_id=line.count_session_id, variance=variance, value=value,
            pct_of_consumption=pct, explained=line.variance_reason is not None,
            significant=significant,
        ))
    return out


def classify_losses(db: Session, ingredient_id: int) -> LossBadge | None:
    """specs-v2-ia-plan-test.md §4 (F5), cible SYN-D. `None` = ni « perte
    récurrente » ni « inhabituel » (y compris si le gate n'est pas atteint).

    Les deux règles sont exclusives et évaluées dans cet ordre : une série
    de pertes n'est pas « inhabituelle », c'est précisément ce que le
    document demande de distinguer (TC-F5-05).

    Motifs d'écart : ils ne participent PAS à la formation de la série (le
    document conditionne celle-ci au seul dépassement de seuil « sur 3
    comptages consécutifs »), mais séparent les deux cumuls rapportés —
    `cumulative_value` inexpliqué, `cumulative_value_total` motifs compris
    (AC-F5-5).
    """
    if not _feature_enabled(db):
        return None
    if not data_gate(db, ingredient_id).ok:
        return None

    obs = _loss_observations(db, ingredient_id)
    if not obs:
        return None

    streak: list[_LossObservation] = []
    for o in reversed(obs):
        if not o.significant:
            break
        streak.append(o)
    streak.reverse()

    if len(streak) >= RECURRING_MIN_STREAK:
        cumul_total = sum(o.value for o in streak)
        cumul_inexplique = sum(o.value for o in streak if not o.explained)
        pct_moyen = sum(o.pct_of_consumption for o in streak) / len(streak)
        return LossBadge(
            ingredient_id=ingredient_id, kind="perte_recurrente",
            cumulative_value=cumul_inexplique, cumulative_value_total=cumul_total,
            streak_length=len(streak),
            explanation=(
                f"écart de {pct_moyen:.0f} % sur {len(streak)} comptages consécutifs, "
                f"soit {cumul_inexplique:.2f} € cumulés inexpliqués"
                + (f" ({cumul_total:.2f} € motifs compris)" if abs(cumul_total - cumul_inexplique) >= 0.005 else "")
            ),
        )

    last = obs[-1]
    if last.significant:
        anterieurs = [o.variance for o in obs[:-1]]
        mediane = statistics.median(anterieurs) if anterieurs else 0.0
        if mediane > 0:
            is_anomaly = last.variance >= mediane * ANOMALY_RATIO
            pourquoi = (
                f"écart de {last.variance:g} contre une médiane historique de "
                f"{mediane:g}, soit {last.variance / mediane:.1f} fois la normale"
            )
        else:
            # Tous les comptages précédents conformes : « 3 × 0 » n'a pas de
            # sens, on retombe sur un seuil relatif (cf. SYN-D).
            is_anomaly = last.pct_of_consumption >= ANOMALY_MIN_PCT
            pourquoi = (
                f"écart de {last.pct_of_consumption:.0f} % de la consommation de la période, "
                f"alors qu'aucun écart n'avait été constaté auparavant"
            )
        if is_anomaly:
            return LossBadge(
                ingredient_id=ingredient_id, kind="inhabituel",
                cumulative_value=0.0 if last.explained else last.value,
                cumulative_value_total=last.value,
                session_id=last.session_id, explanation=pourquoi,
            )

    return None
