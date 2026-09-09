"""F15 — contrôle d'intégrité des ventes importées (Lot IA-1,
docs/feature-plans/ia-f10-f19.md §6). Garde-fou du reste de l'édifice IA :
un import mal calé corromprait le stock théorique et, en cascade, toutes
les prévisions (F5/F6/F9/F10) sans jamais le dire.

Trois capacités indépendantes, toutes non bloquantes — « l'import reste
toujours possible : l'outil alerte, ne bloque pas » — donc aucune ne
touche à une ligne déjà écrite, chacune ne fait que diagnostiquer :

1. `check_import_volume` — le nombre de lignes/le CA/le nombre de plats
   distincts d'un import, comparé au profil habituel du même jour de
   semaine (gate : >= 3 occurrences passées de ce jour, sinon aucun
   faux positif possible — AC-F15-3, TC-F15-04).
2. `detect_missing_days` — un trou dans l'historique (gate : >= 3 semaines
   d'historique global, TC-F15-04) ; un jour de fermeture connu (marqué
   explicitement via `mark_day_closed`, ou détecté comme chroniquement à
   zéro — TC-F15-06) n'est jamais un trou.
3. `find_duplicate_import` — un fichier déjà importé, par empreinte du
   contenu (calculée à la source dans `sales_import.import_sales`).
"""
import hashlib
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service
from app.templating import nom_du_jour

MIN_WEEKDAY_OCCURRENCES = 3  # ia-f10-f19.md §6 : « >= 3 semaines d'imports pour établir une normale »
MIN_HISTORY_DAYS_FOR_GAPS = 21  # 3 semaines, même gate pour le repérage de trous


@dataclass
class VolumeAlert:
    checked_date: date
    metric: str  # "lignes" | "chiffre d'affaires" | "plats distincts"
    actual: float
    typical: float
    deviation_pct: float
    message: str


@dataclass
class VolumeCheckResult:
    ok: bool
    message: str | None
    alerts: list[VolumeAlert] = field(default_factory=list)


@dataclass
class MissingDayAlert:
    start: date
    end: date  # inclusive ; == start pour un jour isolé
    message: str

    @property
    def missing_on(self) -> date:
        """Alias pour le cas courant (un seul jour), le plus fréquent."""
        return self.start

    @property
    def day_count(self) -> int:
        return (self.end - self.start).days + 1


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f15_enabled


def _daily_metrics(db: Session, before: date | None = None) -> dict[date, tuple[int, float, int]]:
    """{date -> (lignes, chiffre d'affaires, plats distincts)}, dérivé de
    TOUTES les ventes connues (pas seulement celles d'un import précis :
    un import réel correspond en général à un seul jour, mais rien
    n'empêche deux fichiers de se recouper sur une même date)."""
    query = db.query(models.SaleLine)
    if before is not None:
        query = query.filter(models.SaleLine.sale_date < before)
    metrics: dict[date, tuple[int, float, list[int | None]]] = {}
    for line in query.all():
        d = line.sale_date.date()
        rows, revenue, dishes = metrics.get(d, (0, 0.0, []))
        rows += 1
        revenue += line.quantity_sold * (line.unit_price or 0.0)
        dishes.append(line.dish_id)
        metrics[d] = (rows, revenue, dishes)
    return {d: (rows, revenue, len(set(dishes) - {None})) for d, (rows, revenue, dishes) in metrics.items()}


def _closed_dates(db: Session) -> set[date]:
    return {c.closed_on for c in db.query(models.ClosedDay).all()}


def check_import_volume(db: Session, sales_import_id: int) -> VolumeCheckResult:
    """docs/feature-plans/ia-f10-f19.md §6 (AC-F15-1). Compare chaque date
    couverte par cet import à la médiane des occurrences PASSÉES du même
    jour de semaine."""
    if not _feature_enabled(db):
        return VolumeCheckResult(ok=False, message="Fonctionnalité F15 désactivée (feature flag éteint).")

    sales_import = db.get(models.SalesImport, sales_import_id)
    if sales_import is None:
        return VolumeCheckResult(ok=False, message="Import introuvable.")

    dates = sorted({line.sale_date.date() for line in sales_import.lines})
    if not dates:
        return VolumeCheckResult(ok=True, message=None, alerts=[])

    settings = settings_service.get_settings(db)
    all_metrics = _daily_metrics(db)
    alerts: list[VolumeAlert] = []

    for d in dates:
        rows, revenue, dish_count = all_metrics.get(d, (0, 0.0, 0))
        historique = [
            all_metrics[past] for past in all_metrics
            if past < d and past.weekday() == d.weekday()
        ]
        if len(historique) < MIN_WEEKDAY_OCCURRENCES:
            continue  # gate non atteint pour ce jour de semaine : aucun avis (AC-F15-3)

        rows_hist = sorted(h[0] for h in historique)
        typique = rows_hist[len(rows_hist) // 2]
        if typique <= 0:
            continue
        deviation = abs(rows - typique) / typique
        if deviation > settings.import_volume_alert_pct / 100.0:
            alerts.append(VolumeAlert(
                checked_date=d, metric="lignes", actual=rows, typical=typique,
                deviation_pct=deviation * 100.0,
                message=(
                    f"Ce fichier contient {rows:g} ventes pour un {nom_du_jour(d)}, "
                    f"contre {typique:g} habituellement. Import incomplet ?"
                ),
            ))

    return VolumeCheckResult(ok=True, message=None, alerts=alerts)


def detect_missing_days(db: Session, *, as_of: date | None = None) -> list[MissingDayAlert]:
    """docs/feature-plans/ia-f10-f19.md §6 (AC-F15-2). Un jour sans aucune
    vente, dans la fenêtre d'historique connue, qui n'est ni marqué fermé
    ni un jour de semaine chroniquement à zéro (TC-F15-06)."""
    if not _feature_enabled(db):
        return []

    metrics = _daily_metrics(db)
    if not metrics:
        return []

    known_dates = sorted(metrics)
    window_start, window_end = known_dates[0], as_of or known_dates[-1]
    if (window_end - window_start).days + 1 < MIN_HISTORY_DAYS_FOR_GAPS:
        return []  # premier import / historique trop court : aucune alerte (TC-F15-04)

    closed = _closed_dates(db)

    # Un jour de semaine "chroniquement fermé" : toutes ses occurrences
    # connues sont à zéro vente, sur au moins MIN_WEEKDAY_OCCURRENCES
    # occurrences — sinon un seul jour férié isolé serait pris pour une
    # fermeture habituelle.
    par_jour_semaine: dict[int, list[int]] = {}
    d = window_start
    while d <= window_end:
        par_jour_semaine.setdefault(d.weekday(), []).append(metrics.get(d, (0, 0.0, 0))[0])
        d += timedelta(days=1)
    jours_fermeture_habituelle = {
        wd for wd, comptes in par_jour_semaine.items()
        if len(comptes) >= MIN_WEEKDAY_OCCURRENCES and all(c == 0 for c in comptes)
    }

    missing_dates: list[date] = []
    d = window_start
    while d <= window_end:
        if (
            d not in metrics
            and d not in closed
            and d.weekday() not in jours_fermeture_habituelle
        ):
            missing_dates.append(d)
        d += timedelta(days=1)

    # TC-F15-05 : des jours manquants consécutifs (une fermeture prolongée,
    # des congés) forment UNE période exceptionnelle, pas N alertes
    # individuelles répétant le même diagnostic jour par jour.
    alerts: list[MissingDayAlert] = []
    i = 0
    while i < len(missing_dates):
        start = missing_dates[i]
        end = start
        while i + 1 < len(missing_dates) and missing_dates[i + 1] == end + timedelta(days=1):
            i += 1
            end = missing_dates[i]
        if start == end:
            message = (
                f"Aucune vente importée pour le {start:%d/%m} ({nom_du_jour(start)}) — "
                f"jour de fermeture ou import oublié ?"
            )
        else:
            nb_jours = (end - start).days + 1
            message = (
                f"Aucune vente importée du {start:%d/%m} au {end:%d/%m} "
                f"({nb_jours} jours) — période de congés ou import oublié ?"
            )
        alerts.append(MissingDayAlert(start=start, end=end, message=message))
        i += 1
    return alerts


def mark_day_closed(db: Session, closed_on: date, reason: str | None = None) -> None:
    """AC-F15-2 : « avec la possibilité de marquer le jour comme fermé ».
    Idempotent : marquer deux fois le même jour ne crée pas de doublon."""
    existing = db.query(models.ClosedDay).filter_by(closed_on=closed_on).one_or_none()
    if existing is not None:
        if reason is not None:
            existing.reason = reason
        db.commit()
        return
    db.add(models.ClosedDay(closed_on=closed_on, reason=reason))
    db.commit()


def find_duplicate_import(db: Session, content: str) -> models.SalesImport | None:
    """« Détection de doublon de fichier déjà prévue en F8, conservée
    ici. » Par empreinte du contenu brut, pas par nom de fichier (qui peut
    changer d'un export à l'autre sans que le contenu change)."""
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return db.query(models.SalesImport).filter_by(content_hash=content_hash).first()
