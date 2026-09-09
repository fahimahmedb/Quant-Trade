"""F22 — gaspillage consolidé et valorisé (Lot IA-2, docs/feature-plans/
backlog-lot-ia-2.md ticket 1). « Combien le gaspillage m'a coûté ce
mois-ci », en euros et en % du chiffre d'affaires — aujourd'hui dispersé
entre les badges de perte (F5, `ai_drift.classify_losses`), les alertes
de péremption à venir (F14) et l'écran d'écarts, sans jamais être
additionné.

Agrège des données DÉJÀ produites par F5/F14/F17, n'invente aucun second
calcul de perte, de risque ou de diagnostic :
- `CountLine.variance`/`variance_value`/`variance_reason` directement
  (pas `ai_drift._loss_observations`, dont le filtre de significativité
  et la logique de série consécutive répondent à une question différente
  — « y a-t-il un problème récurrent » — de celle posée ici — « combien
  ça a coûté au total sur la période », y compris les pertes isolées).
- `ai_variance_diagnosis.diagnose` (F17) en renvoi, jamais un second
  diagnostic parallèle, uniquement pour les ingrédients dont la perte
  inexpliquée sur la période dépasse `Settings.loss_alert_eur` (même
  seuil « perte significative » que F5, pas une nouvelle constante).
- `ai_expiry_risk.assess_expiry_risk` (F14) pour le risque à VENIR —
  reporté SÉPARÉMENT (`at_risk_total`), jamais additionné au gaspillage
  déjà constaté : l'un est un fait passé, l'autre une projection.

Fenêtre : glissante en jours (`Settings.waste_summary_window_days`,
défaut 90 ≈ le mois courant + les deux précédents évoqué par le backlog),
pas un découpage par mois calendaire — décision purement technique
(backlog-lot-ia-2.md §1 règle 4), aucune autre fenêtre temporelle du
projet ne raisonne en mois civils (`COMPARISON_WINDOW_DAYS` de F12 est le
précédent direct).
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import ai_expiry_risk, ai_variance_diagnosis, settings_service


@dataclass
class WasteEntry:
    ingredient_id: int
    ingredient_name: str
    explained_value: float  # motif saisi (casse, périmé, offert...)
    unexplained_value: float  # aucun motif saisi
    hypotheses: list[ai_variance_diagnosis.Hypothesis] = field(default_factory=list)

    @property
    def total_value(self) -> float:
        return self.explained_value + self.unexplained_value


@dataclass
class WasteSummaryResult:
    ok: bool
    message: str | None
    period_start: datetime | None = None
    period_end: datetime | None = None
    revenue: float | None = None
    explained_total: float = 0.0
    unexplained_total: float = 0.0
    at_risk_total: float = 0.0  # F14 : à venir, jamais additionné au reste
    entries: list[WasteEntry] = field(default_factory=list)
    explanation: str = ""

    @property
    def total(self) -> float:
        return self.explained_total + self.unexplained_total

    @property
    def pct_of_revenue(self) -> float | None:
        if not self.revenue:
            return None
        return self.total / self.revenue * 100.0


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f22_enabled


def waste_summary(db: Session, *, end: datetime | None = None) -> WasteSummaryResult:
    """backlog-lot-ia-2.md ticket 1."""
    if not _feature_enabled(db):
        return WasteSummaryResult(ok=False, message="Fonctionnalité F22 désactivée (feature flag éteint).")

    settings = settings_service.get_settings(db)
    end = end or datetime.utcnow()
    start = end - timedelta(days=settings.waste_summary_window_days)

    lines = (
        db.query(models.CountLine)
        .join(models.CountSession)
        .filter(
            models.CountSession.ended_at.isnot(None),
            models.CountSession.ended_at > start,
            models.CountSession.ended_at <= end,
            models.CountLine.counted_quantity.isnot(None),
        )
        .all()
    )

    par_ingredient: dict[int, list[models.CountLine]] = {}
    for line in lines:
        variance = line.variance or 0.0
        if variance <= 0:
            continue  # un surplus n'est pas du gaspillage (même lecture que partout ailleurs)
        par_ingredient.setdefault(line.ingredient_id, []).append(line)

    entries: list[WasteEntry] = []
    explained_total = 0.0
    unexplained_total = 0.0
    for ingredient_id, ing_lines in par_ingredient.items():
        ingredient = ing_lines[0].ingredient
        explained = sum(l.variance_value or 0.0 for l in ing_lines if l.variance_reason is not None)
        unexplained = sum(l.variance_value or 0.0 for l in ing_lines if l.variance_reason is None)
        explained_total += explained
        unexplained_total += unexplained

        hypotheses: list[ai_variance_diagnosis.Hypothesis] = []
        if unexplained >= settings.loss_alert_eur:
            diagnosis = ai_variance_diagnosis.diagnose(db, ingredient_id)
            if diagnosis.gate.ok:
                hypotheses = diagnosis.hypotheses

        entries.append(WasteEntry(
            ingredient_id=ingredient_id, ingredient_name=ingredient.name,
            explained_value=explained, unexplained_value=unexplained, hypotheses=hypotheses,
        ))
    entries.sort(key=lambda e: e.total_value, reverse=True)

    at_risk_total = 0.0
    active_ingredients = db.query(models.Ingredient).filter(
        models.Ingredient.is_active.is_(True), models.Ingredient.shelf_life_days.isnot(None),
    ).all()
    for ingredient in active_ingredients:
        risk = ai_expiry_risk.assess_expiry_risk(db, ingredient.id, today=end)
        if risk.ok and risk.at_risk:
            at_risk_total += risk.value_at_risk or 0.0

    sales = (
        db.query(models.SaleLine)
        .filter(models.SaleLine.sale_date > start, models.SaleLine.sale_date <= end)
        .all()
    )
    revenue = sum(s.quantity_sold * (s.unit_price or 0.0) for s in sales)

    total = explained_total + unexplained_total
    jours = round(settings.waste_summary_window_days)
    if total <= 0:
        explanation = f"Aucune perte constatée sur les {jours} derniers jours."
    else:
        pct = f", soit {total / revenue * 100:.1f} % du chiffre d'affaires" if revenue > 0 else ""
        explanation = (
            f"{total:.2f} € de gaspillage constaté sur les {jours} derniers jours{pct} "
            f"({unexplained_total:.2f} € inexpliqués, {explained_total:.2f} € motivés)."
        )
    if at_risk_total > 0:
        explanation += f" {at_risk_total:.2f} € de stock supplémentaires à risque de péremption si rien ne change."

    return WasteSummaryResult(
        ok=True, message=None, period_start=start, period_end=end,
        revenue=revenue if revenue > 0 else None,
        explained_total=explained_total, unexplained_total=unexplained_total,
        at_risk_total=at_risk_total, entries=entries, explanation=explanation,
    )
