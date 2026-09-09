"""F18 — indicateur de confiance des prévisions, retour automatique à v1
(Lot IA-1, docs/feature-plans/ia-f10-f19.md §9). Le pendant RUNTIME du
backtest IA-01 du Lot IA-0 (`ai_forecast.backtest_vs_v1`) : où IA-01 est
un calcul ponctuel pour décider d'ACTIVER F6, F18 surveille EN CONTINU
une fois F6 actif, et désactive automatiquement si la qualité se dégrade
— « c'est le pendant runtime du test IA-06 », dit le document.

Gate : >= 4 semaines de prévisions produites, y compris en mode ombre —
littéralement le gate déjà posé par `backtest_vs_v1`
(`ai_forecast.BACKTEST_MIN_WEEKS`). Réutilisé tel quel, jamais redéfini
séparément.

Hystérésis (backlog-lot-ia-1 §4 ticket 5, décision actée) : fenêtres
ASYMÉTRIQUES. 3 semaines de dégradation CONSÉCUTIVES désactivent F6 pour
l'ingrédient (AC-F18-1) ; la réactivation exige 3 semaines de recul ET
un NOUVEAU backtest complet redevenu favorable
(`BacktestResult.should_activate`, le même critère qu'IA-01 : >= 15 %
d'amélioration sur >= 4 semaines) — jamais seulement 3 bonnes semaines
consécutives, pour qu'un rebond ponctuel ne réenclenche pas
immédiatement ce que la dégradation venait d'éteindre (TC-F18-05).

Journal (AC-F18-2) : chaque bascule automatique écrite dans
`ModelDecisionLog` — première brique du « journal de décision du
modèle » resté en suspens depuis avancement-lot-ia-0-trois-decisions §1,
construite ici au périmètre strict dont F18 a besoin.

Vocabulaire (AC-F18-3) : aucun terme statistique (MAPE, RMSE) dans les
messages destinés à un usage restaurateur — l'écart est exprimé en
pourcentage clair, jamais le nom de la métrique.
"""
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast, settings_service

DEGRADE_STREAK_WEEKS = 3  # AC-F18-1 : « dégrade sous la v1 sur 3 semaines »
CONFIDENCE_WINDOW_WEEKS = 4  # « écart moyen [...] sur les 4 dernières semaines »


@dataclass
class ConfidenceAssessment:
    ok: bool
    message: str | None
    ingredient_id: int | None = None
    is_reverted_to_v1: bool = False
    average_error_pct: float | None = None
    explanation: str = ""


@dataclass
class ReversionOutcome:
    ok: bool
    message: str | None
    action: str = "none"  # "none" | "reverted_to_v1" | "reactivated"
    detail: str = ""


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f18_enabled


def _log(db: Session, ingredient_id: int, event: str, detail: str) -> None:
    db.add(models.ModelDecisionLog(feature="F18", ingredient_id=ingredient_id, event=event, detail=detail))


def assess_confidence(db: Session, ingredient_id: int) -> ConfidenceAssessment:
    """docs/feature-plans/ia-f10-f19.md §9 : « écart moyen entre prévision
    et réel sur les 4 dernières semaines, en clair » (AC-F18-3 : jamais de
    jargon statistique dans ce message)."""
    if not _feature_enabled(db):
        return ConfidenceAssessment(ok=False, message="Fonctionnalité F18 désactivée (feature flag éteint).")

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return ConfidenceAssessment(ok=False, message="Ingrédient introuvable.")

    backtest = ai_forecast.backtest_vs_v1(db, ingredient_id)
    if not backtest.ok:
        return ConfidenceAssessment(
            ok=False, message=backtest.message, ingredient_id=ingredient_id,
            is_reverted_to_v1=ingredient.f6_reverted_to_v1,
        )

    recentes = backtest.weekly_results[-CONFIDENCE_WINDOW_WEEKS:]
    erreur_moyenne = sum(w.mape_f6 for w in recentes) / len(recentes) * 100.0

    explanation = f"Prévisions justes à ±{erreur_moyenne:.0f} % en moyenne sur les {len(recentes)} dernières semaines."
    if ingredient.f6_reverted_to_v1:
        explanation += " Retour temporaire à la méthode habituelle pour cet ingrédient."

    return ConfidenceAssessment(
        ok=True, message=None, ingredient_id=ingredient_id,
        is_reverted_to_v1=ingredient.f6_reverted_to_v1,
        average_error_pct=erreur_moyenne, explanation=explanation,
    )


def check_and_apply_reversion(db: Session, ingredient_id: int) -> ReversionOutcome:
    """Le contrôle runtime lui-même — à invoquer périodiquement pour un
    ingrédient (aucun ordonnanceur dans ce projet : comme le reste de
    F5-F18, une fonction pure à appeler, jamais une tâche de fond)."""
    if not _feature_enabled(db):
        return ReversionOutcome(ok=False, message="Fonctionnalité F18 désactivée (feature flag éteint).")

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return ReversionOutcome(ok=False, message="Ingrédient introuvable.")

    backtest = ai_forecast.backtest_vs_v1(db, ingredient_id)
    if not backtest.ok:
        return ReversionOutcome(ok=False, message=backtest.message)

    dernieres = backtest.weekly_results[-DEGRADE_STREAK_WEEKS:]
    degrade_trois_semaines = (
        len(dernieres) >= DEGRADE_STREAK_WEEKS and all(not w.f6_better for w in dernieres)
    )

    if not ingredient.f6_reverted_to_v1:
        if degrade_trois_semaines:
            ingredient.f6_reverted_to_v1 = True
            detail = (
                f"F6 sous la v1 sur {DEGRADE_STREAK_WEEKS} semaines consécutives "
                f"({', '.join(f'{w.week_start:%d/%m}' for w in dernieres)}) : retour à la v1."
            )
            _log(db, ingredient_id, "revert_to_v1", detail)
            db.commit()
            return ReversionOutcome(ok=True, message=None, action="reverted_to_v1", detail=detail)
        return ReversionOutcome(ok=True, message=None, action="none")

    # Déjà revenu à la v1 : la réactivation exige un backtest COMPLET
    # redevenu favorable, pas seulement quelques bonnes semaines locales
    # (hystérésis, TC-F18-05).
    if backtest.should_activate:
        ingredient.f6_reverted_to_v1 = False
        detail = (
            f"Nouveau backtest complet favorable (gain {backtest.improvement:.0%} sur "
            f"{backtest.weeks_evaluated} semaines) : réactivation de F6."
        )
        _log(db, ingredient_id, "reactivated", detail)
        db.commit()
        return ReversionOutcome(ok=True, message=None, action="reactivated", detail=detail)

    return ReversionOutcome(ok=True, message=None, action="none")
