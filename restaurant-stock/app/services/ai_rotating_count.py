"""F11 — comptage tournant intelligent ⭐ (Lot IA-1, docs/feature-plans/
ia-f10-f19.md §2). Le document la juge lui-même la plus précieuse des dix
extensions : « la seule fonctionnalité IA du projet qui s'attaque
directement à la friction n°1 [...] elle réduit ce que le chef FAIT ».

Gate : F10 actif (le sien : >= 4 semaines de ventes, par ingrédient) ET
>= 3 comptages complets AU GLOBAL — une normale de stabilité n'a de sens
qu'une fois quelques comptages réellement observés.

Précédence, du plus fort au plus faible :
1. Badge F5 actif (perte récurrente OU inhabituel) — réintègre TOUJOURS
   l'ingrédient dans la session du jour, même retiré manuellement
   (TC-F11-07 : la sécurité prime la préférence).
2. Comptage complet obligatoire en retard (>= `full_count_interval_days`,
   défaut 28 j, depuis le dernier comptage terminé) — la session du jour
   EST alors l'ensemble des ingrédients actifs, aucune session ciblée
   n'est proposée tant qu'il n'est pas fait (AC-F11-3).
3. Choix manuel du chef (`set_manual_override`), mémorisé.
4. Fréquence calculée (criticité F10 x stabilité).

Interprétation faute de spec formelle sur le stockage — aucune notion de
« session ciblée » n'existe dans le schéma v1 : `counting.start_count_session`
pré-remplit déjà une ligne par ingrédient ACTIF pour CHAQUE session (section
5 du brief), sans distinction partielle/complète. « Comptage complet » au
sens de cette fonctionnalité = n'importe quelle `CountSession` terminée
(`ended_at` renseigné) : `daily_session()` ne fait que RECOMMANDER quels
ingrédients demander aujourd'hui, un filtre d'affichage pour un futur
écran — jamais un nouveau type d'enregistrement ici.

Grille fréquence x criticité, partiellement spécifiée par le document
(seuls les deux coins extrêmes sont donnés : « fort coût + instable ->
quotidien », « faible coût + toujours conforme -> mensuel ») : le milieu
de la grille est comblé en degradant vers PLUS de comptage plutôt que
moins dans le doute — un défaut de sécurité (jamais un jugement métier sur
CE qui est prioritaire, à la différence du seuil de volatilité de F10, où
un tel défaut n'existe pas). Documenté ligne par ligne dans `_frequency_for`.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import ai_criticality, ai_drift, settings_service
from app.templating import pluriel

MIN_GLOBAL_COMPLETED_COUNTS = 3  # ia-f10-f19.md §2 : « >= 3 comptages complets »
# Fenêtre de référence explicitement citée par le document lui-même, dans
# son propre exemple de message : « conforme sur les 6 derniers comptages ».
CONFORMING_STREAK_REFERENCE = 6
FREQUENCY_DAYS = {"quotidien": 1, "hebdomadaire": 7, "mensuel": 28}


@dataclass
class FrequencySuggestion:
    ingredient_id: int
    frequency: str  # "quotidien" | "hebdomadaire" | "mensuel"
    criticality_class: str | None
    conforming_streak: int
    explanation: str


@dataclass
class DailySessionItem:
    ingredient_id: int
    ingredient_name: str
    included: bool
    reason: str  # "badge_f5" | "comptage_complet_du" | "manuel" | "frequence"
    frequency: FrequencySuggestion


@dataclass
class DailySessionResult:
    ok: bool
    message: str | None
    items: list[DailySessionItem] = field(default_factory=list)
    full_count_required: bool = False
    full_count_overdue_days: float | None = None


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f11_enabled


def _global_completed_count_sessions(db: Session) -> int:
    return db.query(models.CountSession).filter(models.CountSession.ended_at.isnot(None)).count()


def _last_full_count_at(db: Session) -> datetime | None:
    """Cf. docstring : « comptage complet » = n'importe quelle CountSession
    terminée, faute de distinction partielle/complète dans le schéma v1."""
    session = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at.desc())
        .first()
    )
    return session.ended_at if session else None


def _conforming_streak(db: Session, ingredient_id: int) -> int:
    """Nombre de comptages consécutifs les plus récents où l'écart de cet
    ingrédient n'a pas franchi le seuil de significativité de F5
    (`Settings.loss_alert_pct`/`loss_alert_eur`, réutilisés tels quels —
    backlog-lot-ia-1 §2 règle 1 : pas de nouveau seuil pour un concept déjà
    défini)."""
    settings = settings_service.get_settings(db)
    lines = (
        db.query(models.CountLine)
        .join(models.CountSession)
        .filter(
            models.CountLine.ingredient_id == ingredient_id,
            models.CountSession.ended_at.isnot(None),
            models.CountLine.counted_quantity.isnot(None),
        )
        .order_by(models.CountSession.ended_at.desc())
        .all()
    )
    streak = 0
    for line in lines:
        variance = line.variance or 0.0
        value = line.variance_value or 0.0
        consumption_pct = line.variance_pct or 0.0
        significant = variance > 0 and (
            value >= settings.loss_alert_eur or abs(consumption_pct) >= settings.loss_alert_pct
        )
        if significant:
            break
        streak += 1
    return streak


def _frequency_for(criticality_class: str | None, streak: int) -> str:
    """Voir docstring de tête pour la justification du remplissage du
    milieu de grille. Cas traités, dans l'ordre :
    - non déterminé / dormant / pas encore assez de comptages (streak < 3,
      TC-F11-06) -> quotidien : jamais moins de vigilance sur l'inconnu.
    - classe A (critique), stable (>= 6 comptages conformes, la fenêtre de
      référence du document) -> hebdomadaire : un ingrédient à fort coût
      ne descend jamais à mensuel, même conforme — seul le « faible coût »
      de l'exemple du document atteint mensuel.
    - classe A, pas encore assez stable -> quotidien (le coin explicite du
      document : « fort coût + instable »).
    - classe B ou C, stable (>= 6) -> mensuel (l'autre coin explicite :
      « faible coût + toujours conforme »).
    - classe B ou C, stabilité intermédiaire -> hebdomadaire (le défaut de
      sécurité du milieu de grille).
    """
    if criticality_class is None or criticality_class == "dormant" or streak < MIN_GLOBAL_COMPLETED_COUNTS:
        return "quotidien"
    if criticality_class == "A":
        return "hebdomadaire" if streak >= CONFORMING_STREAK_REFERENCE else "quotidien"
    return "mensuel" if streak >= CONFORMING_STREAK_REFERENCE else "hebdomadaire"


def suggest_frequency(
    db: Session, ingredient_id: int, *, as_of: date | None = None,
    criticality: ai_criticality.CriticalityResult | None = None,
) -> FrequencySuggestion:
    """`criticality` : résultat déjà calculé de `ai_criticality.classify_ingredients`,
    à fournir par un appelant qui traite plusieurs ingrédients (voir
    `daily_session`) pour ne pas relancer tout le classement Pareto à
    chaque ingrédient — recalculé ici seulement si absent, pour un appel
    autonome sur un seul ingrédient."""
    if criticality is None:
        criticality = ai_criticality.classify_ingredients(db, as_of=as_of)
    item = None
    if criticality.ok:
        item = next((it for it in criticality.items if it.ingredient_id == ingredient_id), None)
    classe = item.effective_class if item else None

    streak = _conforming_streak(db, ingredient_id)
    frequence = _frequency_for(classe, streak)

    ingredient = db.get(models.Ingredient, ingredient_id)
    valeur = item.annual_value if item else None
    part = f", {valeur:.2f} € par an" if valeur is not None else ""
    explanation = (
        f"{ingredient.name} — comptée {frequence} : "
        + (f"conforme sur les {streak} derniers comptages" if streak else "pas encore de comptage conforme établi")
        + part
    )
    return FrequencySuggestion(
        ingredient_id=ingredient_id, frequency=frequence, criticality_class=classe,
        conforming_streak=streak, explanation=explanation,
    )


def daily_session(db: Session, *, as_of: date | None = None) -> DailySessionResult:
    """docs/feature-plans/ia-f10-f19.md §2 (SYN-K)."""
    if not _feature_enabled(db):
        return DailySessionResult(ok=False, message="Fonctionnalité F11 désactivée (feature flag éteint).")
    if not settings_service.get_settings(db).feature_f10_enabled:
        return DailySessionResult(ok=False, message="F11 nécessite F10 (classification de criticité) activé.")
    if _global_completed_count_sessions(db) < MIN_GLOBAL_COMPLETED_COUNTS:
        n = _global_completed_count_sessions(db)
        return DailySessionResult(
            ok=False,
            message=f"{n} comptage{pluriel(n)} complet{pluriel(n)} sur {MIN_GLOBAL_COMPLETED_COUNTS} nécessaires",
        )

    as_of_dt = datetime.combine(as_of, datetime.min.time()) if as_of else datetime.utcnow()
    settings = settings_service.get_settings(db)

    dernier_complet = _last_full_count_at(db)
    overdue_days = None
    full_count_required = False
    if dernier_complet is not None:
        overdue_days = (as_of_dt - dernier_complet).days
        full_count_required = overdue_days >= settings.full_count_interval_days

    ingredients = db.query(models.Ingredient).filter_by(is_active=True).order_by(models.Ingredient.name).all()
    overrides = {o.ingredient_id: o.include for o in db.query(models.DailySessionOverride).all()}
    criticality = ai_criticality.classify_ingredients(db, as_of=as_of)

    items: list[DailySessionItem] = []
    for ing in ingredients:
        frequence = suggest_frequency(db, ing.id, as_of=as_of, criticality=criticality)
        badge = ai_drift.classify_losses(db, ing.id)  # None si F5 éteint ou pas de badge

        if badge is not None:
            included, reason = True, "badge_f5"
        elif full_count_required:
            included, reason = True, "comptage_complet_du"
        elif ing.id in overrides:
            included, reason = overrides[ing.id], "manuel"
        else:
            due_days = FREQUENCY_DAYS[frequence.frequency]
            derniere_fois = _last_ingredient_count_at(db, ing.id)
            if derniere_fois is None:
                included = True  # jamais compté : dû par défaut
            else:
                included = (as_of_dt - derniere_fois).days >= due_days
            reason = "frequence"

        items.append(DailySessionItem(
            ingredient_id=ing.id, ingredient_name=ing.name, included=included,
            reason=reason, frequency=frequence,
        ))

    if not items:
        return DailySessionResult(ok=False, message="Aucun ingrédient actif.")

    return DailySessionResult(
        ok=True, message=None, items=items,
        full_count_required=full_count_required, full_count_overdue_days=overdue_days,
    )


def _last_ingredient_count_at(db: Session, ingredient_id: int) -> datetime | None:
    line = (
        db.query(models.CountLine)
        .join(models.CountSession)
        .filter(
            models.CountLine.ingredient_id == ingredient_id,
            models.CountSession.ended_at.isnot(None),
            models.CountLine.counted_quantity.isnot(None),
        )
        .order_by(models.CountSession.ended_at.desc())
        .first()
    )
    return line.count_session.ended_at if line else None


def set_manual_override(db: Session, ingredient_id: int, include: bool | None) -> None:
    """TC-F11-07 : le retrait (ou l'ajout) manuel d'un ingrédient est
    mémorisé. `include=None` efface le forçage (retour à la fréquence
    calculée)."""
    existing = db.query(models.DailySessionOverride).filter_by(ingredient_id=ingredient_id).one_or_none()
    if include is None:
        if existing is not None:
            db.delete(existing)
            db.commit()
        return
    if existing is not None:
        existing.include = include
    else:
        db.add(models.DailySessionOverride(ingredient_id=ingredient_id, include=include))
    db.commit()
