"""Écran de comparaison en mode ombre (backlog-lot-ia-1.md §1/§6) :
surface d'authentification séparée de la session établissement (jeton
`RESTAURANT_STOCK_INTERNAL_ADMIN_TOKEN`, jamais la session restaurateur).

`monkeypatch.setattr(config, "INTERNAL_ADMIN_TOKEN", ...)` plutôt qu'une
variable d'environnement : `app/config.py` lit la variable une seule fois
à l'import, une variable d'environnement changée après coup ne serait
jamais relue.
"""
from app import config, models
from app.services import ai_forecast, settings_service
from tests import synthetic_data as syn

ADMIN_PATH = "/admin/comparaison-ia"


def test_returns_404_without_any_token_configured(anonymous_client, monkeypatch):
    monkeypatch.setattr(config, "INTERNAL_ADMIN_TOKEN", None)

    response = anonymous_client.client.get(ADMIN_PATH)

    assert response.status_code == 404


def test_returns_404_with_a_wrong_token(anonymous_client, monkeypatch):
    monkeypatch.setattr(config, "INTERNAL_ADMIN_TOKEN", "le-bon-jeton")

    response = anonymous_client.client.get(ADMIN_PATH, params={"token": "un-autre-jeton"})

    assert response.status_code == 404


def test_correct_token_grants_access_without_any_restaurant_session(anonymous_client, monkeypatch):
    """Non-vacuité de la séparation des deux surfaces d'authentification :
    AUCUNE session établissement ici (anonymous_client), et l'accès
    fonctionne quand même — le jeton seul suffit."""
    monkeypatch.setattr(config, "INTERNAL_ADMIN_TOKEN", "le-bon-jeton")

    response = anonymous_client.client.get(ADMIN_PATH, params={"token": "le-bon-jeton"})

    assert response.status_code == 200
    assert "admin_token" in response.cookies


def test_cookie_from_a_prior_request_grants_access_without_the_query_param(anonymous_client, monkeypatch):
    monkeypatch.setattr(config, "INTERNAL_ADMIN_TOKEN", "le-bon-jeton")
    premiere = anonymous_client.client.get(ADMIN_PATH, params={"token": "le-bon-jeton"})
    assert premiere.status_code == 200

    seconde = anonymous_client.client.get(ADMIN_PATH)  # pas de ?token= cette fois, cookie déjà posé

    assert seconde.status_code == 200


def test_a_logged_in_restaurant_account_does_not_get_access_on_its_own(seeded_client, monkeypatch):
    """Non-vacuité par contre-exemple : un restaurateur bel et bien
    connecté sur son propre compte ne doit JAMAIS voir cet écran, même en
    devinant l'URL — la session établissement n'est pas un jeton valide."""
    monkeypatch.setattr(config, "INTERNAL_ADMIN_TOKEN", "le-bon-jeton")

    response = seeded_client.client.get(ADMIN_PATH)

    assert response.status_code == 404


def test_shows_backtest_comparison_per_active_ingredient(anonymous_client, monkeypatch):
    monkeypatch.setattr(config, "INTERNAL_ADMIN_TOKEN", "le-bon-jeton")
    with anonymous_client.session_factory() as db:
        result = syn.build_syn_a(db, seed=1, weeks=12)
        settings_service.get_settings(db)
        settings = db.get(models.Settings, 1)
        settings.feature_f6_enabled = True
        db.commit()
        backtest = ai_forecast.backtest_vs_v1(db, result.ingredient.id)
        assert backtest.ok, backtest.message  # sinon ce test ne prouve rien

    response = anonymous_client.client.get(ADMIN_PATH, params={"token": "le-bon-jeton"})

    assert response.status_code == 200
    assert result.ingredient.name in response.text
    assert f"{backtest.improvement * 100:.0f}" in response.text
