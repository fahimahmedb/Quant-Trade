from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.flash import redirect
from app.forms import InvalidNumberError, parse_float_fr
from app.services import counting
from app.templating import pluriel, templates

router = APIRouter(prefix="/counting", tags=["counting"])


@router.get("")
def counting_home(request: Request, db: Session = Depends(get_db)):
    open_session = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.is_(None))
        .order_by(models.CountSession.started_at.desc())
        .first()
    )
    history = (
        db.query(models.CountSession)
        .filter(models.CountSession.ended_at.isnot(None))
        .order_by(models.CountSession.ended_at.desc())
        .limit(10)
        .all()
    )
    return templates.TemplateResponse(request,
        "counting/home.html",
        {"request": request, "open_session": open_session, "history": history},
    )


@router.post("/start")
def start_session(counted_by: str = Form(""), db: Session = Depends(get_db)):
    session = counting.start_count_session(db, counted_by=counted_by.strip() or None)
    if not session.lines:
        return redirect(
            "/counting",
            "Aucun ingrédient actif à compter — ajoutez d'abord vos ingrédients.",
            error=True,
        )
    return redirect(f"/counting/{session.id}", "Comptage démarré.")


@router.get("/{session_id}")
def counting_session_view(session_id: int, request: Request, db: Session = Depends(get_db)):
    session = db.get(models.CountSession, session_id)
    if session is None:
        return redirect("/counting", "Session de comptage introuvable.", error=True)
    if session.is_completed:
        return redirect(f"/counting/{session_id}/summary")

    zones = list(models.StorageZone)
    lines_by_zone = {zone: [] for zone in zones}
    for line in session.lines:
        lines_by_zone[line.ingredient.storage_zone].append(line)
    for zone_lines in lines_by_zone.values():
        zone_lines.sort(key=lambda line: line.ingredient.name)

    counted = sum(1 for line in session.lines if line.counted_quantity is not None)
    return templates.TemplateResponse(request,
        "counting/session.html",
        {
            "request": request,
            "session": session,
            "zones": zones,
            "lines_by_zone": lines_by_zone,
            "reasons": list(models.VarianceReason),
            "counted": counted,
            "total": len(session.lines),
            "revision": counting.session_revision(db, session_id),
        },
    )


@router.post("/{session_id}/zone/{zone}")
async def save_zone(
    session_id: int, zone: models.StorageZone, request: Request, db: Session = Depends(get_db)
):
    session = db.get(models.CountSession, session_id)
    if session is None or session.is_completed:
        return redirect("/counting", "Session de comptage introuvable ou déjà close.", error=True)

    form = await request.form()
    entries = []
    for line in session.lines:
        if line.ingredient.storage_zone != zone:
            continue
        raw_value = form.get(f"count_{line.id}")
        if raw_value is None or raw_value.strip() == "":
            continue
        try:
            counted_quantity = parse_float_fr(raw_value)
        except InvalidNumberError:
            continue
        raw_reason = form.get(f"reason_{line.id}") or ""
        try:
            reason = models.VarianceReason(raw_reason) if raw_reason else None
        except ValueError:
            reason = None
        entries.append(counting.CountEntry(
            line_id=line.id,
            counted_quantity=counted_quantity,
            variance_reason=reason,
            entered_at=_client_time(form.get(f"entered_at_{line.id}")),
        ))

    result = counting.apply_entries(db, session_id, entries)
    n = len(result.applied)
    return redirect(
        f"/counting/{session_id}#zone-{zone.value}",
        f"{n} ligne{pluriel(n)} enregistrée{pluriel(n)} — {zone.label}.",
        alerts=_conflict_message(result.conflicts),
    )


def _client_time(raw) -> datetime | None:
    """Horodatage de saisie envoyé par l'appareil (millisecondes epoch).

    Ignoré s'il est absurde (horloge déréglée, valeur future) : mieux vaut
    retomber sur l'heure du serveur que dater une saisie de 2037.
    """
    try:
        moment = datetime.utcfromtimestamp(float(raw) / 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return None
    now = datetime.utcnow()
    if moment > now + timedelta(minutes=5) or moment < now - timedelta(days=30):
        return None
    return moment


def _conflict_message(conflicts: list[dict]) -> str | None:
    if not conflicts:
        return None
    details = ", ".join(
        f"{c['ingredient']} (valeur conservée : {c['kept']})" for c in conflicts
    )
    n = len(conflicts)
    return (
        f"{n} ligne{pluriel(n)} modifiée{pluriel(n)} entre-temps depuis un autre appareil, "
        f"votre saisie plus ancienne n'a pas été appliquée : {details}"
    )


@router.post("/{session_id}/sync")
async def sync_offline_entries(session_id: int, request: Request, db: Session = Depends(get_db)):
    """Vidage de la file hors-ligne (F3). Renvoie du JSON, pas une page :
    appelé par le script de la page de comptage à la reconnexion."""
    payload = await request.json()
    session = db.get(models.CountSession, session_id)
    if session is None:
        return JSONResponse({"error": "Session de comptage introuvable."}, status_code=404)

    entries = []
    for raw in payload.get("entries", []):
        try:
            reason_value = raw.get("variance_reason") or ""
            reason = models.VarianceReason(reason_value) if reason_value else None
        except ValueError:
            reason = None
        try:
            entries.append(counting.CountEntry(
                line_id=int(raw["line_id"]),
                counted_quantity=float(raw["counted_quantity"]),
                variance_reason=reason,
                entered_at=_client_time(raw.get("entered_at")),
            ))
        except (KeyError, TypeError, ValueError):
            continue

    try:
        result = counting.apply_entries(db, session_id, entries)
    except counting.SessionClosedError:
        # Comptage clos depuis un autre appareil pendant qu'on était hors-ligne.
        # Le stock a déjà été recalé : on refuse d'écrire et on le dit, plutôt
        # que de laisser des lignes comptées sans mouvement correspondant.
        return JSONResponse(
            {
                "error": "Comptage déjà terminé depuis un autre appareil, "
                         "vos saisies en attente n'ont pas été appliquées.",
                "closed": True,
                "stale": True,
                "revision": counting.session_revision(db, session_id),
            },
            status_code=409,
        )

    completed = False
    if payload.get("complete"):
        counting.complete_count_session(
            db, session_id, ended_at=_client_time(payload.get("ended_at"))
        )
        completed = True

    revision = counting.session_revision(db, session_id)
    sent_revision = payload.get("revision")
    return JSONResponse({
        "applied": len(result.applied),
        "unknown": result.unknown,
        "completed": completed,
        "revision": revision,
        # Page servie par le cache alors que les fiches ont bougé : la liste
        # affichée n'est plus celle du serveur, il faut la recharger.
        "stale": bool(sent_revision) and sent_revision != revision and not completed,
        "conflicts": [
            {"ingredient": c["ingredient"], "kept": c["kept"], "discarded": c["discarded"]}
            for c in result.conflicts
        ],
    })


@router.post("/{session_id}/complete")
async def complete_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    session = db.get(models.CountSession, session_id)
    if session is None:
        return redirect("/counting", "Session de comptage introuvable.", error=True)
    form = await request.form()
    counting.complete_count_session(
        db, session_id, ended_at=_client_time(form.get("ended_at"))
    )
    return redirect(f"/counting/{session_id}/summary", "Comptage terminé, stock théorique recalé.")


@router.get("/{session_id}/summary")
def session_summary(session_id: int, request: Request, db: Session = Depends(get_db)):
    session = db.get(models.CountSession, session_id)
    if session is None:
        return redirect("/counting", "Session de comptage introuvable.", error=True)
    report = counting.variance_report(db, session_id)
    total_value = sum(line.variance_value or 0 for line in report)
    return templates.TemplateResponse(request,
        "counting/summary.html",
        {"request": request, "session": session, "report": report, "total_value": total_value},
    )
