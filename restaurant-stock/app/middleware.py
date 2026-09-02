"""Protection des écrans par session (F2, AC-F2-1).

Fermé par défaut : toute route qui n'est pas explicitement publique exige
une session valide. Un oubli côté routeur donne donc une redirection vers
la connexion, jamais une page métier ouverte.
"""
import logging
import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from app.database import SessionLocal
from app.services import auth

logger = logging.getLogger("app.errors")


def _session_factory(request):
    """Fabrique de sessions de l'application ; les tests y injectent la leur."""
    return getattr(request.app.state, "session_factory", None) or SessionLocal

PUBLIC_PATHS = {"/login", "/setup", "/healthz"}
PUBLIC_PREFIXES = ("/static/",)


def _is_public(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES) or path == "/favicon.ico"


class RequireLoginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if _is_public(path):
            return await call_next(request)

        db = _session_factory(request)()
        try:
            account = auth.read_session(db, request.cookies.get(auth.SESSION_COOKIE))
            # Tant qu'aucun compte n'existe, tout mène à la création du compte.
            if account is None:
                destination = "/setup" if not auth.account_exists(db) else "/login"
        finally:
            db.close()

        if account is None:
            if destination == "/login" and path != "/":
                # Retour à l'écran demandé après reconnexion (TC-F2-03).
                destination = f"/login?next={path}"
            return RedirectResponse(destination, status_code=303)

        request.state.account = account
        return await call_next(request)


class ErrorLogMiddleware(BaseHTTPMiddleware):
    """Journalise les erreurs applicatives (F2) sans jamais les masquer.

    L'exception est enregistrée puis relancée : le comportement observable
    ne change pas (page d'erreur du serveur, trace dans les logs), on gagne
    seulement un journal consultable par l'équipe projet.
    """

    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            self._record(request, exc)
            raise

    @staticmethod
    def _record(request, exc: Exception) -> None:
        from app import models

        logger.exception("Erreur non gérée sur %s %s", request.method, request.url.path)
        db = _session_factory(request)()
        try:
            db.add(models.ErrorLog(
                method=request.method,
                path=request.url.path,  # sans query string : pas de donnée saisie
                error_type=type(exc).__name__,
                message=str(exc)[:1000],
                traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-8000:],
            ))
            db.commit()
        except Exception:  # journaliser ne doit jamais aggraver l'incident
            logger.exception("Impossible d'enregistrer l'erreur dans le journal")
            db.rollback()
        finally:
            db.close()
