"""Écrans réservés à l'équipe projet, jamais au restaurateur (backlog-lot-
ia-1.md §1/§6). Surface d'authentification volontairement SÉPARÉE de la
session établissement (app/routers/auth.py) : un jeton dédié
(`RESTAURANT_STOCK_INTERNAL_ADMIN_TOKEN`), jamais la session d'un compte
restaurant — un restaurateur connecté sur son propre compte ne doit
jamais, même en devinant l'URL, atterrir ici. Exempté de
`RequireLoginMiddleware` (app/middleware.py, préfixe `/admin/`) pour cette
même raison : la session établissement n'a pas de sens sur cette surface.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.services import ai_shadow_comparison
from app.templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_TOKEN_COOKIE = "admin_token"


def require_admin_token(request: Request, token: str | None = Query(None)) -> str:
    """404, jamais 401/403 : un jeton absent ou faux rend la page
    introuvable, exactement comme si elle n'existait pas (backlog §6 :
    « à protéger comme tel, pas seulement caché derrière un lien » — un
    401/403 confirmerait au contraire que la route existe)."""
    expected = config.INTERNAL_ADMIN_TOKEN
    supplied = token or request.cookies.get(ADMIN_TOKEN_COOKIE)
    if not expected or supplied != expected:
        raise HTTPException(status_code=404)
    return supplied


@router.get("/comparaison-ia")
def comparaison_ia(
    request: Request, db: Session = Depends(get_db), token: str = Depends(require_admin_token),
):
    response = templates.TemplateResponse(request,
        "admin/comparaison_ia.html",
        {"request": request, "comparisons": ai_shadow_comparison.shadow_mode_comparison(db)},
    )
    # Le jeton passé une fois en query string est repris en cookie : pas
    # besoin de le recopier à chaque rechargement de l'écran. Secure
    # seulement si la requête est réellement en HTTPS (même règle que
    # app/routers/auth.py) : en http local, un cookie Secure ne serait
    # jamais renvoyé.
    secure = config.SESSION_COOKIE_SECURE and request.url.scheme == "https"
    response.set_cookie(
        ADMIN_TOKEN_COOKIE, token, max_age=60 * 60 * 8, httponly=True,
        samesite="strict", secure=secure, path="/admin",
    )
    return response
