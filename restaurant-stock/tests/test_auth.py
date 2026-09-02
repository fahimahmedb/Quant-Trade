"""F2 — authentification (AC-F2-1, TC-F2-01, TC-F2-02, TC-F2-03)."""
from datetime import datetime, timedelta

import pytest

from app import models
from app.services import auth
from tests.conftest import TEST_EMAIL, TEST_PASSWORD

BUSINESS_SCREENS = [
    "/", "/ingredients", "/ingredients/new", "/recipes", "/recipes/new",
    "/sales/import", "/counting", "/deliveries", "/deliveries/new",
    "/variance", "/orders", "/metrics", "/settings",
]


# AC-F2-1 ------------------------------------------------------------------
def test_ac_f2_1_no_business_screen_is_reachable_without_a_session(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)

    for path in BUSINESS_SCREENS:
        r = client.get(path)
        assert r.url.path == "/login", f"{path} accessible sans session"
        assert "Connexion" in r.text


def test_ac_f2_1_write_endpoints_are_protected_too(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)

    r = client.post("/ingredients/new", data={
        "name": "Intrus", "unit": "g", "unit_cost": "1", "storage_zone": "sec",
        "current_theoretical_stock": "1", "alert_threshold": "",
    })
    assert r.url.path == "/login"
    with sessions() as db:
        assert db.query(models.Ingredient).count() == 0


def test_uploaded_delivery_photos_are_not_public(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)
    r = client.get("/uploads/quelconque.png")
    assert r.url.path == "/login"


def test_without_any_account_everything_leads_to_setup(anonymous_client):
    client = anonymous_client.client
    for path in ["/", "/counting", "/login"]:
        assert client.get(path).url.path == "/setup"


def test_setup_creates_the_account_and_opens_a_session(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    r = client.post("/setup", data={
        "email": "chef@bistrot.fr", "password": "motdepasse123",
        "restaurant_name": "Le Bistrot",
    })
    assert r.status_code == 200
    assert r.url.path == "/"  # connecté dans la foulée
    with sessions() as db:
        account = db.query(models.Account).one()
        assert account.email == "chef@bistrot.fr"
        assert account.restaurant_name == "Le Bistrot"
        assert "motdepasse123" not in account.password_hash  # jamais en clair

    # Un second passage par /setup ne peut pas créer de compte supplémentaire.
    r = client.post("/setup", data={"email": "autre@bistrot.fr", "password": "motdepasse123",
                                    "restaurant_name": ""})
    with sessions() as db:
        assert db.query(models.Account).count() == 1


def test_setup_refuses_short_password_and_invalid_email(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    r = client.post("/setup", data={"email": "chef@bistrot.fr", "password": "court", "restaurant_name": ""})
    assert r.status_code == 422 and "8 caractères" in r.text
    r = client.post("/setup", data={"email": "pas-un-email", "password": "motdepasse123", "restaurant_name": ""})
    assert r.status_code == 422 and "invalide" in r.text
    with sessions() as db:
        assert db.query(models.Account).count() == 0


# TC-F2-01 -----------------------------------------------------------------
def test_tc_f2_01_nominal_login_then_access_and_logout(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)

    r = client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD, "next": "/"})
    assert r.status_code == 200 and r.url.path == "/"
    assert client.get("/ingredients").url.path == "/ingredients"

    r = client.post("/logout")
    assert r.url.path == "/login"
    assert client.get("/ingredients").url.path == "/login"


def test_login_is_case_insensitive_on_email(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)
    r = client.post("/login", data={"email": "  CHEF@Bistrot.FR ", "password": TEST_PASSWORD, "next": "/"})
    assert r.url.path == "/"


def test_login_rejects_wrong_password_without_leaking_account_existence(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)

    known = client.post("/login", data={"email": TEST_EMAIL, "password": "faux", "next": "/"})
    unknown = client.post("/login", data={"email": "inconnu@x.fr", "password": "faux", "next": "/"})
    assert known.status_code == unknown.status_code == 401
    assert "Identifiants incorrects." in known.text and "Identifiants incorrects." in unknown.text


# TC-F2-02 -----------------------------------------------------------------
def test_tc_f2_02_five_wrong_passwords_trigger_a_lockout(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)

    for _ in range(4):
        r = client.post("/login", data={"email": TEST_EMAIL, "password": "faux", "next": "/"})
        assert "Identifiants incorrects." in r.text
    r = client.post("/login", data={"email": TEST_EMAIL, "password": "faux", "next": "/"})
    assert "Trop de tentatives" in r.text

    # Même le bon mot de passe est refusé pendant la temporisation.
    r = client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD, "next": "/"})
    assert r.status_code == 401 and "Trop de tentatives" in r.text

    with sessions() as db:
        account = db.query(models.Account).one()
        assert account.locked_until is not None
        account.locked_until = datetime.utcnow() - timedelta(seconds=1)  # temporisation écoulée
        db.commit()
    r = client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD, "next": "/"})
    assert r.status_code == 200 and r.url.path == "/"


def test_successful_login_resets_the_failure_counter(db_session):
    auth.create_account(db_session, email=TEST_EMAIL, password=TEST_PASSWORD)
    for _ in range(3):
        with pytest.raises(auth.AuthError):
            auth.authenticate(db_session, email=TEST_EMAIL, password="faux")
    assert db_session.query(models.Account).one().failed_attempts == 3

    auth.authenticate(db_session, email=TEST_EMAIL, password=TEST_PASSWORD)
    assert db_session.query(models.Account).one().failed_attempts == 0


# TC-F2-03 -----------------------------------------------------------------
def test_tc_f2_03_expired_session_returns_to_login_and_keeps_the_counting_draft(anonymous_client):
    """Session expirée : retour à la connexion, puis le comptage en cours est
    retrouvé intact (les lignes déjà saisies sont côté serveur)."""
    from app import seed

    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)
        seed.seed_demo(db)
    client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD, "next": "/"})

    r = client.post("/counting/start", data={"counted_by": "Marie"})
    session_id = int(r.url.path.rstrip("/").split("/")[-1])
    with sessions() as db:
        line = (db.query(models.CountLine)
                .filter_by(count_session_id=session_id)
                .join(models.Ingredient).order_by(models.Ingredient.name).first())
        line_id, zone = line.id, line.ingredient.storage_zone.value
    client.post(f"/counting/{session_id}/zone/{zone}", data={f"count_{line_id}": "42"})

    # Expiration : le cookie ne vaut plus rien.
    client.cookies.clear()
    r = client.get(f"/counting/{session_id}")
    assert r.url.path == "/login"
    assert f"next=/counting/{session_id}" in str(r.history[0].headers.get("location", ""))

    client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD,
                                "next": f"/counting/{session_id}"})
    page = client.get(f"/counting/{session_id}")
    assert page.status_code == 200
    with sessions() as db:
        assert db.get(models.CountLine, line_id).counted_quantity == 42
        assert db.get(models.CountSession, session_id).ended_at is None  # toujours en cours


def test_session_cookie_is_httponly_and_expires_in_30_days(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)
    r = client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD, "next": "/"})

    cookie_header = next(
        value for key, value in r.history[0].headers.items()
        if key.lower() == "set-cookie" and auth.SESSION_COOKIE in value
    )
    assert "HttpOnly" in cookie_header
    assert f"Max-Age={30 * 86400}" in cookie_header


def _token_issued_days_ago(account, days: int, monkeypatch) -> str:
    """Jeton signé avec un horodatage daté, pour éprouver la limite des 30 jours."""
    from itsdangerous.timed import TimestampSigner

    original = TimestampSigner.get_timestamp
    monkeypatch.setattr(
        TimestampSigner, "get_timestamp",
        lambda self: original(self) - days * 86400,
    )
    token = auth.issue_session(account)
    monkeypatch.undo()
    return token


def test_session_older_than_thirty_days_is_rejected(db_session, monkeypatch):
    account = auth.create_account(db_session, email=TEST_EMAIL, password=TEST_PASSWORD)

    assert auth.read_session(db_session, _token_issued_days_ago(account, 29, monkeypatch)) is not None
    assert auth.read_session(db_session, _token_issued_days_ago(account, 31, monkeypatch)) is None


def test_tampered_or_missing_token_is_rejected(db_session):
    account = auth.create_account(db_session, email=TEST_EMAIL, password=TEST_PASSWORD)
    token = auth.issue_session(account)
    assert auth.read_session(db_session, None) is None
    assert auth.read_session(db_session, "") is None
    assert auth.read_session(db_session, token[:-3] + "abc") is None


def test_login_does_not_redirect_to_an_external_site(anonymous_client):
    client, sessions = anonymous_client.client, anonymous_client.session_factory
    with sessions() as db:
        auth.create_account(db, email=TEST_EMAIL, password=TEST_PASSWORD)
    r = client.post("/login", data={"email": TEST_EMAIL, "password": TEST_PASSWORD,
                                    "next": "//evil.example.com/"})
    assert r.url.path == "/"


def test_password_hashing_is_salted_and_verifiable():
    first, second = auth.hash_password("motdepasse123"), auth.hash_password("motdepasse123")
    assert first != second  # sel aléatoire
    assert auth.verify_password("motdepasse123", first)
    assert not auth.verify_password("motdepasse124", first)
    assert not auth.verify_password("motdepasse123", "format-invalide")
