"""F15 — contrôle d'intégrité des ventes importées (docs/feature-plans/
ia-f10-f19.md §6), prouvée sur SYN-O. Éteinte par défaut
(`Settings.feature_f15_enabled`).
"""
from datetime import date, datetime, timedelta

from app import models
from app.services import ai_import_integrity, sales_import, settings_service
from tests import synthetic_data as syn


def _enable_f15(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f15_enabled = True
    db.commit()


def test_f15_is_inert_by_default(db_session):
    result = syn.build_syn_o(db_session)
    latest = db_session.query(models.SalesImport).order_by(models.SalesImport.id.desc()).first()

    volume = ai_import_integrity.check_import_volume(db_session, latest.id)
    gaps = ai_import_integrity.detect_missing_days(db_session, as_of=result.end.date())

    assert not volume.ok
    assert "désactivée" in volume.message
    assert gaps == []


# ==========================================================================
# AC-F15-1 — écart de volume détecté, avec un seuil réglable
# ==========================================================================

def test_syn_o_low_volume_day_is_flagged(db_session):
    result = syn.build_syn_o(db_session)
    _enable_f15(db_session)
    latest = db_session.query(models.SalesImport).order_by(models.SalesImport.id.desc()).first()

    outcome = ai_import_integrity.check_import_volume(db_session, latest.id)

    assert outcome.ok, outcome.message
    par_date = {a.checked_date: a for a in outcome.alerts}
    assert result.low_volume_day in par_date
    alerte = par_date[result.low_volume_day]
    assert alerte.actual == result.low_volume_actual
    assert alerte.typical == result.low_volume_typical
    assert "Import incomplet" in alerte.message
    assert f"{result.low_volume_actual:g}" in alerte.message
    assert f"{result.low_volume_typical:g}" in alerte.message


def test_syn_o_normal_days_are_never_flagged(db_session):
    """Non-vacuité par contre-exemple : sans ce test, un code qui alerte
    TOUJOURS passerait le test précédent aussi."""
    result = syn.build_syn_o(db_session)
    _enable_f15(db_session)
    latest = db_session.query(models.SalesImport).order_by(models.SalesImport.id.desc()).first()

    outcome = ai_import_integrity.check_import_volume(db_session, latest.id)

    dates_alertees = {a.checked_date for a in outcome.alerts}
    assert dates_alertees == {result.low_volume_day}


def test_volume_alert_threshold_is_configurable(db_session):
    """§8 des specs V2 : seuil réglable, pas une constante figée. Un jour à
    -20% ne doit pas alerter au seuil par défaut (40%), mais doit alerter
    dès que le seuil descend sous 20%."""
    ing = syn.ingredient(db_session, "Ingrédient seuil", stock_qty=10_000_000.0)
    plat = syn.dish(db_session, "Plat seuil", {ing.id: 1.0})
    start = datetime(2026, 1, 5)  # lundi
    rows = []
    for semaine in range(5):
        d = start + timedelta(days=semaine * 7)
        n = 8 if semaine == 4 else 10  # -20% la dernière semaine
        for _ in range(n):
            rows.append((d, plat.name, 1.0, 5.0))
    syn.import_sales_rows(db_session, rows, filename="seuil.csv")
    latest = db_session.query(models.SalesImport).order_by(models.SalesImport.id.desc()).first()
    _enable_f15(db_session)

    par_defaut = ai_import_integrity.check_import_volume(db_session, latest.id)
    assert par_defaut.alerts == []

    settings = db_session.get(models.Settings, 1)
    settings.import_volume_alert_pct = 15.0
    db_session.commit()

    plus_sensible = ai_import_integrity.check_import_volume(db_session, latest.id)
    assert len(plus_sensible.alerts) == 1


# ==========================================================================
# AC-F15-2 / TC-F15-05 — jours manquants, isolés ou groupés en période
# ==========================================================================

def test_syn_o_isolated_missing_day_is_reported_as_a_single_day(db_session):
    result = syn.build_syn_o(db_session)
    _enable_f15(db_session)

    gaps = ai_import_integrity.detect_missing_days(db_session, as_of=result.end.date())

    par_debut = {g.start: g for g in gaps}
    assert result.missing_day in par_debut
    trou = par_debut[result.missing_day]
    assert trou.end == result.missing_day
    assert trou.day_count == 1
    assert "fermeture ou import oublié" in trou.message


def test_tc_f15_05_a_two_week_vacation_is_one_alert_not_fourteen(db_session):
    result = syn.build_syn_o(db_session)
    _enable_f15(db_session)

    gaps = ai_import_integrity.detect_missing_days(db_session, as_of=result.end.date())

    conges = next(g for g in gaps if g.start == result.vacation_start)
    assert conges.end == result.vacation_end
    assert conges.day_count == 14
    assert "congés" in conges.message
    assert len(gaps) == 2, "un trou isolé + une période de congés, jamais 15 alertes séparées"


def test_ac_f15_2_marking_a_day_closed_removes_its_alert(db_session):
    result = syn.build_syn_o(db_session)
    _enable_f15(db_session)

    avant = ai_import_integrity.detect_missing_days(db_session, as_of=result.end.date())
    assert any(g.start == result.missing_day for g in avant)

    ai_import_integrity.mark_day_closed(db_session, result.missing_day, reason="Fermeture exceptionnelle")

    apres = ai_import_integrity.detect_missing_days(db_session, as_of=result.end.date())
    assert not any(g.start == result.missing_day for g in apres)
    assert any(g.start == result.vacation_start for g in apres), "les congés restent signalés, non affectés"


def test_mark_day_closed_is_idempotent(db_session):
    syn.build_syn_o(db_session)
    ai_import_integrity.mark_day_closed(db_session, date(2026, 2, 9), reason="Premier motif")
    ai_import_integrity.mark_day_closed(db_session, date(2026, 2, 9), reason="Motif corrigé")

    closed = db_session.query(models.ClosedDay).filter_by(closed_on=date(2026, 2, 9)).all()
    assert len(closed) == 1
    assert closed[0].reason == "Motif corrigé"


def test_tc_f15_04_first_import_produces_no_gap_alert(db_session):
    """Moins de 3 semaines d'historique : aucune alerte, jamais de faux
    positif sur un import qui vient tout juste de démarrer. Un vrai trou
    (le 7/01, sans aucune vente) est délibérément présent dans la fenêtre :
    sans le gate, il serait détecté — c'est précisément lui que le gate
    doit supprimer tant que l'historique est trop court pour dire si c'est
    une fermeture normale ou un import oublié."""
    ing = syn.ingredient(db_session, "Ingrédient premier import", stock_qty=10_000_000.0)
    plat = syn.dish(db_session, "Plat premier import", {ing.id: 1.0})
    start = datetime(2026, 1, 5)
    rows = [(start + timedelta(days=d), plat.name, 1.0, 5.0) for d in [0, 1]]  # 5/01, 6/01 ; 7/01 absent
    syn.import_sales_rows(db_session, rows, filename="premier.csv")
    _enable_f15(db_session)

    gaps = ai_import_integrity.detect_missing_days(db_session, as_of=date(2026, 1, 7))
    assert gaps == []


def test_tc_f15_06_a_habitually_closed_weekday_never_triggers_a_gap_alert(db_session):
    """Un restaurant fermé tous les lundis : l'absence de vente le lundi
    n'est jamais un "trou", c'est la normale."""
    ing = syn.ingredient(db_session, "Ingrédient fermeture hebdo", stock_qty=10_000_000.0)
    plat = syn.dish(db_session, "Plat fermeture hebdo", {ing.id: 1.0})
    start = datetime(2026, 1, 5)  # lundi
    rows = []
    for day_offset in range(42):  # 6 semaines
        d = start + timedelta(days=day_offset)
        if d.weekday() == 0:  # lundi fermé
            continue
        rows.append((d, plat.name, 1.0, 5.0))
    syn.import_sales_rows(db_session, rows, filename="fermeture_hebdo.csv")
    _enable_f15(db_session)

    gaps = ai_import_integrity.detect_missing_days(db_session, as_of=(start + timedelta(days=41)).date())
    assert gaps == [], "les lundis, systématiquement sans vente, ne doivent jamais être signalés"


# ==========================================================================
# Détection de doublon de fichier (F8, conservée ici par F15)
# ==========================================================================

def test_find_duplicate_import_detects_the_same_content(db_session):
    syn.ingredient(db_session, "Ingrédient doublon", stock_qty=10_000_000.0)
    contenu = "date,plat,quantite,prix_unitaire\n2026-01-05,Plat X,1.000,5.00\n"
    imported, _ = sales_import.import_sales(db_session, "fichier.csv", contenu)

    doublon = ai_import_integrity.find_duplicate_import(db_session, contenu)
    assert doublon is not None
    assert doublon.id == imported.id


def test_find_duplicate_import_returns_none_for_new_content(db_session):
    syn.ingredient(db_session, "Ingrédient pas doublon", stock_qty=10_000_000.0)
    sales_import.import_sales(
        db_session, "fichier.csv", "date,plat,quantite,prix_unitaire\n2026-01-05,Plat X,1.000,5.00\n",
    )
    autre = ai_import_integrity.find_duplicate_import(
        db_session, "date,plat,quantite,prix_unitaire\n2026-01-06,Plat Y,2.000,6.00\n",
    )
    assert autre is None
