"""F20 — signaux calendaires (docs/feature-plans/backlog-lot-ia-2.md
ticket 4, cible SYN-R). Chaque scénario a été vérifié empiriquement
(script autonome, base en mémoire) avant d'écrire l'assertion dessus —
en particulier la valeur EXACTE du facteur mesuré, qui n'est PAS
exactement le facteur injecté dans le jeu : F6 lui-même intègre, sans le
savoir, les jours fériés tombés dans sa propre fenêtre du jour de
semaine (les 8 dernières occurrences), ce qui légèrement gonfle sa
propre estimation "habituelle" pour ce jour de semaine — un effet réel,
pas une erreur d'arrondi, vérifié avant d'écrire les seuils de
tolérance ci-dessous.
"""
from datetime import date, datetime, timedelta

from app import models
from app.services import ai_calendar_signals as cal, french_calendar, settings_service
from tests import synthetic_data as syn


def _enable(db, *, f20=True, f6=True):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    if f6:
        settings.feature_f6_enabled = True
    if f20:
        settings.feature_f20_enabled = True
    db.commit()


def _flat_sales_with_boost(db, name: str, *, start: date, end: date, base_qty: float, boosted_dates: set[date], boost_factor: float):
    ing = syn.ingredient(db, name, stock_qty=10_000_000.0)
    plat = syn.dish(db, f"Plat {name}", {ing.id: 1.0})
    rows = []
    d = start
    while d <= end:
        qty = base_qty * boost_factor if d in boosted_dates else base_qty
        rows.append((datetime(d.year, d.month, d.day), plat.name, qty, None))
        d += timedelta(days=1)
    syn.import_sales_rows(db, rows, filename=f"{name}.csv")
    return ing


def test_f20_is_inert_by_default(db_session):
    result = syn.build_syn_r(db_session)
    _enable(db_session, f20=False)

    out = cal.adjusted_forecast(db_session, result.ingredient.id, result.target_date)

    assert not out.ok and "désactivée" in out.message


# ==========================================================================
# Signal "férié" — SYN-R
# ==========================================================================

def test_public_holiday_factor_measured_on_syn_r(db_session):
    result = syn.build_syn_r(db_session)
    _enable(db_session)

    out = cal.adjusted_forecast(db_session, result.ingredient.id, result.target_date)

    assert out.ok, out.message
    assert out.adjustment.signal == "ferie"
    assert out.adjustment.occurrences_used == 9  # 9 fériés 2026 strictement avant le 11 novembre
    # Le facteur mesuré est proche du facteur injecté (1,5) sans lui être
    # identique (cf. docstring du module) — vérifié empiriquement à 1,49.
    assert 1.3 < out.adjustment.factor < 1.6
    assert out.adjusted_expected_qty > out.base_expected_qty
    assert "ferie" in out.explanation


def test_target_date_is_not_also_in_a_vacation_period(db_session):
    """Non-vacuité de l'isolation du signal : si le 11 novembre tombait
    aussi dans une période de vacances scolaires embarquée, ce test (et
    celui du dessus) ne prouveraient plus qu'un signal "férié" isolé."""
    assert not french_calendar.is_school_vacation(date(2026, 11, 11), None)
    assert not french_calendar.is_school_vacation(date(2026, 11, 11), "A")
    assert not french_calendar.is_school_vacation(date(2026, 11, 11), "B")
    assert not french_calendar.is_school_vacation(date(2026, 11, 11), "C")


def test_below_threshold_no_adjustment_applied(db_session):
    """Un seul férié passé (1er janvier) avant le 6 avril (Lundi de
    Pâques) : sous le seuil de 3 occurrences, l'estimation habituelle
    doit rester inchangée."""
    holidays_2026 = french_calendar.public_holidays(2026)
    ing = _flat_sales_with_boost(
        db_session, "Sous le seuil", start=date(2026, 1, 1), end=date(2026, 4, 6),
        base_qty=20.0, boosted_dates=holidays_2026, boost_factor=1.5,
    )
    _enable(db_session)

    out = cal.adjusted_forecast(db_session, ing.id, date(2026, 4, 6))

    assert out.ok, out.message
    assert out.adjustment.occurrences_used == 1
    assert out.adjustment.factor is None
    assert out.adjusted_expected_qty == out.base_expected_qty


def test_exactly_three_occurrences_is_the_minimum_that_still_adjusts(db_session):
    """Non-vacuité de la frontière : exactement 3 fériés passés (1er
    janvier, 6 avril, 1er mai) avant le 8 mai doivent suffire à
    déclencher l'ajustement — le seuil est "< 3 : rien", pas "<= 3"."""
    holidays_2026 = french_calendar.public_holidays(2026)
    ing = _flat_sales_with_boost(
        db_session, "Exactement trois", start=date(2026, 1, 1), end=date(2026, 5, 8),
        base_qty=20.0, boosted_dates=holidays_2026, boost_factor=1.5,
    )
    _enable(db_session)

    out = cal.adjusted_forecast(db_session, ing.id, date(2026, 5, 8))

    assert out.adjustment.occurrences_used == 3
    assert out.adjustment.factor is not None
    assert out.adjusted_expected_qty > out.base_expected_qty


# ==========================================================================
# Signal "exceptionnel" — marquage manuel
# ==========================================================================

def test_exceptional_day_marking_works_independently_of_f20_flag(db_session):
    ing = syn.ingredient(db_session, "Marquage sans F20", stock_qty=1000.0)
    _enable(db_session, f20=False, f6=False)  # F20 ET F6 éteints

    entry = cal.mark_exceptional_day(db_session, date(2026, 3, 15), note="concert")

    assert entry.on_date == date(2026, 3, 15)
    assert entry.note == "concert"


def test_exceptional_day_factor_measured_from_past_markings(db_session):
    start = date(2026, 1, 5)  # lundi
    exceptional_thursdays = {start + timedelta(days=3 + 7 * w) for w in range(6)}
    ing = _flat_sales_with_boost(
        db_session, "Jeudis exceptionnels", start=start, end=start + timedelta(weeks=8),
        base_qty=20.0, boosted_dates=exceptional_thursdays, boost_factor=2.0,
    )
    _enable(db_session)
    for d in sorted(exceptional_thursdays):
        cal.mark_exceptional_day(db_session, d, note="concert")

    target = max(exceptional_thursdays)
    out = cal.adjusted_forecast(db_session, ing.id, target)

    assert out.ok, out.message
    assert out.adjustment.signal == "exceptionnel"
    assert out.adjustment.occurrences_used == 5  # les 5 jeudis précédents, jamais la cible elle-même
    assert out.adjusted_expected_qty > out.base_expected_qty


def test_unmark_exceptional_day_removes_the_signal(db_session):
    cal.mark_exceptional_day(db_session, date(2026, 3, 15), note="concert")

    cal.unmark_exceptional_day(db_session, date(2026, 3, 15))

    remaining = db_session.query(models.ExceptionalDay).filter_by(on_date=date(2026, 3, 15)).one_or_none()
    assert remaining is None


def test_exceptional_signal_takes_priority_over_public_holiday(db_session):
    """Non-vacuité de la priorité (docstring du module) : le 1er janvier
    est TOUJOURS férié — marqué en plus comme exceptionnel, le signal
    retenu doit rester "exceptionnel", jamais "ferie"."""
    cal.mark_exceptional_day(db_session, date(2026, 1, 1), note="nouvel an spécial")
    exceptional_dates = {row.on_date for row in db_session.query(models.ExceptionalDay).all()}

    signal = cal._signal_for_date(date(2026, 1, 1), exceptional_dates, None)

    assert signal == "exceptionnel"


def test_public_holiday_signal_without_any_exceptional_marking(db_session):
    """Non-vacuité par contre-exemple direct : sans marquage, ce même
    jour doit rester "ferie" — la priorité ne doit rien changer quand
    "exceptionnel" n'est pas en jeu."""
    signal = cal._signal_for_date(date(2026, 1, 1), set(), None)

    assert signal == "ferie"


# ==========================================================================
# Signal "vacances" — dépendance à la zone
# ==========================================================================

def test_zone_specific_vacation_requires_the_matching_zone_setting(db_session):
    d = date(2026, 2, 10)  # dans les vacances d'hiver de la zone A seulement
    assert not french_calendar.is_school_vacation(d, None)
    assert french_calendar.is_school_vacation(d, "A")
    assert not french_calendar.is_school_vacation(d, "B")
    assert not french_calendar.is_school_vacation(d, "C")


def test_common_vacation_detected_even_without_a_zone(db_session):
    """Toussaint est commune aux 3 zones : détectée même sans
    `school_vacation_zone` réglé (dégradation silencieuse, backlog §1
    règle 2 — seule la partie ZONE du signal reste inerte sans zone)."""
    d = date(2026, 10, 20)  # Toussaint 2026, toutes zones
    assert french_calendar.is_school_vacation(d, None)
