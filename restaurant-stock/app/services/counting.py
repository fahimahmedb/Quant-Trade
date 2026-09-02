"""Comptage physique et écart théorique/réel (sections 4.4, 4.5, 5)."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services import stock


def start_count_session(db: Session, counted_by: str | None = None) -> models.CountSession:
    """Crée une session et pré-remplit une ligne par ingrédient actif avec le
    stock théorique courant — le cuisinier confirme ou corrige, il ne ressaisit
    pas depuis zéro (section 5)."""
    session = models.CountSession(counted_by=counted_by)
    db.add(session)
    db.flush()

    ingredients = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.is_active.is_(True))
        .order_by(models.Ingredient.storage_zone, models.Ingredient.name)
        .all()
    )
    for ingredient in ingredients:
        db.add(
            models.CountLine(
                count_session_id=session.id,
                ingredient_id=ingredient.id,
                theoretical_quantity=ingredient.current_theoretical_stock,
            )
        )
    db.commit()
    db.refresh(session)
    return session


def confirm_count_line(
    db: Session,
    line_id: int,
    counted_quantity: float,
    variance_reason: models.VarianceReason | None = None,
    entered_at: datetime | None = None,
) -> models.CountLine:
    line = db.get(models.CountLine, line_id)
    if line is None:
        raise ValueError(f"Ligne de comptage introuvable : {line_id}")
    line.counted_quantity = counted_quantity
    line.variance_reason = variance_reason
    line.confirmed_at = entered_at or datetime.utcnow()
    db.commit()
    db.refresh(line)
    return line


@dataclass
class CountEntry:
    """Saisie d'une ligne, éventuellement faite hors-ligne (F3).

    `entered_at` est l'heure de la saisie sur l'appareil, pas celle de
    l'arrivée au serveur : c'est elle qui départage deux appareils.
    """

    line_id: int
    counted_quantity: float
    variance_reason: models.VarianceReason | None = None
    entered_at: datetime | None = None


class SessionClosedError(RuntimeError):
    """Session closée pendant qu'un appareil était hors-ligne.

    Le stock théorique a déjà été recalé sur les valeurs de la clôture :
    écrire de nouvelles quantités laisserait des lignes comptées sans
    mouvement de stock correspondant. On refuse, et on le dit.
    """


@dataclass
class SyncResult:
    applied: list[int] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    unknown: list[int] = field(default_factory=list)


def apply_entries(db: Session, session_id: int, entries: list[CountEntry]) -> SyncResult:
    """Applique des saisies, la plus récente par ligne l'emportant (F3).

    Une saisie plus ancienne que celle déjà enregistrée pour la même ligne
    n'écrase rien et ressort en conflit : jamais de fusion silencieuse.
    """
    session = db.get(models.CountSession, session_id)
    if session is None:
        raise ValueError(f"Session de comptage introuvable : {session_id}")
    if session.is_completed:
        raise SessionClosedError(session_id)

    lines = {line.id: line for line in session.lines}
    result = SyncResult()
    for entry in entries:
        line = lines.get(entry.line_id)
        if line is None:
            result.unknown.append(entry.line_id)
            continue

        entered_at = entry.entered_at or datetime.utcnow()
        if line.confirmed_at is not None and line.confirmed_at > entered_at:
            result.conflicts.append({
                "line_id": line.id,
                "ingredient": line.ingredient.name,
                "kept": line.counted_quantity,
                "discarded": entry.counted_quantity,
                "kept_at": line.confirmed_at,
            })
            continue

        line.counted_quantity = entry.counted_quantity
        line.variance_reason = entry.variance_reason
        line.confirmed_at = entered_at
        result.applied.append(line.id)

    db.commit()
    return result


def complete_count_session(
    db: Session, session_id: int, ended_at: datetime | None = None
) -> models.CountSession:
    """Clôture la session : le stock réel confirmé devient le nouveau stock
    théorique de référence pour chaque ingrédient compté."""
    session = db.get(models.CountSession, session_id)
    if session is None:
        raise ValueError(f"Session de comptage introuvable : {session_id}")

    for line in session.lines:
        if line.counted_quantity is None:
            continue
        delta = line.counted_quantity - line.ingredient.current_theoretical_stock
        if delta != 0:
            stock.record_movement(
                db,
                line.ingredient,
                models.MovementType.COMPTAGE,
                delta,
                reference=f"comptage#{session.id}",
            )

    # `ended_at` fourni = heure réelle de fin sur l'appareil : une session
    # terminée hors-ligne et synchronisée plus tard garde une durée juste (F3).
    session.ended_at = ended_at or datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


def variance_report(db: Session, session_id: int) -> list[models.CountLine]:
    """Lignes comptées de la session, triées par écart en valeur (€) décroissant."""
    session = db.get(models.CountSession, session_id)
    if session is None:
        raise ValueError(f"Session de comptage introuvable : {session_id}")
    counted = [line for line in session.lines if line.counted_quantity is not None]
    counted.sort(key=lambda line: abs(line.variance_value or 0), reverse=True)
    return counted


def session_revision(db: Session, session_id: int) -> str:
    """Empreinte de la liste affichée par la page de comptage (F3).

    Une page servie par le cache du service worker peut dater : une fiche
    renommée, déplacée de zone ou changée d'unité entre-temps, ou la session
    close depuis un autre appareil. L'empreinte change dans ces cas, ce qui
    permet de prévenir « liste mise à jour » plutôt que de laisser compter sur
    un écran faux. Les quantités saisies n'y entrent pas : elles bougent à
    chaque enregistrement et rendraient l'empreinte inutilisable.
    """
    session = db.get(models.CountSession, session_id)
    if session is None:
        raise ValueError(f"Session de comptage introuvable : {session_id}")

    parts = [f"closed={session.is_completed}"]
    for line in sorted(session.lines, key=lambda item: item.id):
        ing = line.ingredient
        parts.append(
            f"{line.id}|{ing.name}|{ing.unit.value}|{ing.storage_zone.value}"
        )
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return digest[:16]
