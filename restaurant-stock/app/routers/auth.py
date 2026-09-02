"""Écrans de connexion et de création du compte établissement (F2)."""
from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.config import SESSION_COOKIE_SECURE, SESSION_MAX_AGE_DAYS
from app.database import get_db
from app.flash import redirect
from app.services import auth
from app.templating import templates

router = APIRouter(tags=["auth"])


def _with_session_cookie(request: Request, response, token: str):
    # Secure dès que la requête est en HTTPS (production, cf. README : servir
    # derrière un reverse proxy TLS avec --proxy-headers). En http local, un
    # cookie Secure ne serait jamais renvoyé par le navigateur.
    secure = SESSION_COOKIE_SECURE and request.url.scheme == "https"
    response.set_cookie(
        auth.SESSION_COOKIE,
        token,
        max_age=SESSION_MAX_AGE_DAYS * 86400,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/login")
def login_form(request: Request, db: Session = Depends(get_db)):
    if not auth.account_exists(db):
        return redirect("/setup")
    return templates.TemplateResponse(
        request, "auth/login.html",
        {"request": request, "next": request.query_params.get("next", "/"), "error": None},
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_db),
):
    try:
        account = auth.authenticate(db, email=email, password=password)
    except auth.AuthError as exc:
        return templates.TemplateResponse(
            request, "auth/login.html",
            {"request": request, "next": next, "error": str(exc), "email": email},
            status_code=401,
        )
    # `next` doit rester interne : on ne redirige jamais vers un site externe.
    destination = next if next.startswith("/") and not next.startswith("//") else "/"
    return _with_session_cookie(
        request, redirect(destination, "Connecté."), auth.issue_session(account)
    )


@router.post("/logout")
def logout():
    response = redirect("/login", "Déconnecté.")
    response.delete_cookie(auth.SESSION_COOKIE, path="/")
    return response


@router.get("/setup")
def setup_form(request: Request, db: Session = Depends(get_db)):
    if auth.account_exists(db):
        return redirect("/login")
    return templates.TemplateResponse(request, "auth/setup.html", {"request": request, "error": None})


@router.post("/setup")
def setup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    restaurant_name: str = Form(""),
    db: Session = Depends(get_db),
):
    if auth.account_exists(db):
        return redirect("/login", "Un compte existe déjà.", error=True)
    try:
        account = auth.create_account(
            db, email=email, password=password, restaurant_name=restaurant_name
        )
    except auth.AuthError as exc:
        return templates.TemplateResponse(
            request, "auth/setup.html",
            {"request": request, "error": str(exc), "email": email,
             "restaurant_name": restaurant_name},
            status_code=422,
        )
    return _with_session_cookie(
        request, redirect("/", "Compte créé, bienvenue."), auth.issue_session(account)
    )
