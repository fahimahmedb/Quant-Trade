"""F25 — indicateur de confiance étendu à toutes les recommandations IA
(Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 3).
`metrics.suggestion_adoption_stats` (v1) ne mesure que l'adoption des
suggestions de commande (F7). Ce module étend le MÊME mécanisme
(`SuggestionDecision` : acceptée/modifiée/rejetée) à F13 (prévision de
mise en place) — referme le gap documenté au ticket 9 du Lot IA-1
(« mémorisation prévision/décision réelle », resté sans spec faute
d'AC/TC).

`ProductionSuggestion` reprend le schéma d'`OrderSuggestionLine` (F7) —
suggested_quantity/final_quantity/decision/validated_at, même
`SuggestionDecision` — sans le concept de lot (`OrderSuggestionBatch`) :
F13 génère une suggestion par appel, par ingrédient, jamais une fournée
quotidienne comme F7.

Vue agrégée PAR FONCTIONNALITÉ (F7, F13), jamais un total global qui
masquerait qu'un restaurateur suit F7 à la lettre tout en ignorant F13 —
« taux d'adoption réel des recommandations IA par les cuisiniers »,
contexte métier §11.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import ai_production_forecast, metrics, settings_service


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f25_enabled


def record_production_suggestion(db: Session, ingredient_id: int) -> models.ProductionSuggestion | None:
    """Appelle F13 (`ai_production_forecast.forecast_production`, jamais
    un second calcul) et journalise sa sortie en attente de décision.
    `None` si F13 lui-même reste inactif pour cet ingrédient (feature
    flag F13, marqueur « préparé en interne », gate F6...) — rien à
    journaliser, dégradation silencieuse comme partout ailleurs dans le
    projet."""
    if not _feature_enabled(db):
        return None

    forecast = ai_production_forecast.forecast_production(db, ingredient_id)
    if not forecast.ok:
        return None

    suggestion = models.ProductionSuggestion(
        ingredient_id=ingredient_id, window_days=forecast.window_days,
        suggested_quantity=forecast.suggested_quantity,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


def record_decision(
    db: Session, suggestion_id: int, *, decision: models.SuggestionDecision,
    final_quantity: float | None = None,
) -> models.ProductionSuggestion:
    """La décision RÉELLE du chef (accepte/modifie/rejette) — c'est cette
    comparaison suggéré/réel que le backlog appelle « mémorisation ».
    Jamais gatée par le feature flag F25 : une fois une suggestion
    journalisée, la décision qui la clôt doit toujours pouvoir s'enregistrer,
    même si le flag a été éteint entre-temps (même principe que confirmer
    une ligne de comptage déjà ouverte, ailleurs dans le projet)."""
    suggestion = db.get(models.ProductionSuggestion, suggestion_id)
    if suggestion is None:
        raise ValueError(f"Suggestion de production introuvable : {suggestion_id}")
    suggestion.decision = decision
    suggestion.final_quantity = final_quantity
    suggestion.validated_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


def _production_adoption_stats(db: Session) -> metrics.AdoptionStats:
    lines = db.query(models.ProductionSuggestion).all()
    counts = {d: 0 for d in models.SuggestionDecision}
    for line in lines:
        counts[line.decision] += 1
    return metrics.AdoptionStats(
        total=len(lines), acceptee=counts[models.SuggestionDecision.ACCEPTEE],
        modifiee=counts[models.SuggestionDecision.MODIFIEE],
        rejetee=counts[models.SuggestionDecision.REJETEE],
        en_attente=counts[models.SuggestionDecision.EN_ATTENTE],
    )


def adoption_stats_by_feature(db: Session) -> dict[str, metrics.AdoptionStats]:
    """F7 toujours présent (v1, `metrics.suggestion_adoption_stats`,
    jamais gatée, inchangée ici). F13 seulement si F25 est actif — sa clé
    est ABSENTE (pas un zéro) quand F25 est éteint, pour que « la
    fonctionnalité n'a jamais été activée » reste visiblement distinct de
    « activée, mais jamais encore utilisée »."""
    stats: dict[str, metrics.AdoptionStats] = {"F7": metrics.suggestion_adoption_stats(db)}
    if _feature_enabled(db):
        stats["F13"] = _production_adoption_stats(db)
    return stats
