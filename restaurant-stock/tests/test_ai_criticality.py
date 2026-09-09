"""F10 — classification de criticité des ingrédients (docs/feature-plans/
ia-f10-f19.md §1), prouvée sur SYN-J. Éteinte par défaut
(`Settings.feature_f10_enabled`).
"""
from datetime import datetime, timedelta

import pytest

from app import models
from app.services import ai_criticality, settings_service
from tests import synthetic_data as syn


def _enable_f10(db):
    settings_service.get_settings(db)
    settings = db.get(models.Settings, 1)
    settings.feature_f10_enabled = True
    db.commit()


def test_f10_is_inert_by_default(db_session):
    syn.build_syn_j(db_session)
    result = ai_criticality.classify_ingredients(db_session)
    assert not result.ok
    assert "désactivée" in result.message
    assert result.items == []


# ==========================================================================
# SYN-J — répartition de valeur Pareto connue
# ==========================================================================

def test_syn_j_the_three_big_ingredients_are_class_a(db_session):
    result = syn.build_syn_j(db_session)
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())

    assert outcome.ok, outcome.message
    par_id = {it.ingredient_id: it for it in outcome.items}
    for gros in result.gros:
        assert par_id[gros.id].effective_class == "A", gros.name


def test_syn_j_no_small_ingredient_is_ever_class_a(db_session):
    """AC-F10-1 : la classification retrouve la répartition injectée — les
    17 petits (petit-grand compris) cumulent volontairement au-delà de 80%
    dès le premier d'entre eux ajouté : aucun ne doit jamais être classé A,
    quel que soit l'ordre de tri entre ex-æquo."""
    result = syn.build_syn_j(db_session)
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())

    par_id = {it.ingredient_id: it for it in outcome.items}
    petits = [result.petit_grand] + result.petits_small
    for petit in petits:
        assert par_id[petit.id].effective_class != "A", petit.name


def test_syn_j_summary_names_the_class_a_ingredients_never_bare_letters(db_session):
    """Le document interdit d'afficher A/B/C seules : formulation métier
    obligatoire (« X ingrédients représentent 80% de votre coût matière »)."""
    syn.build_syn_j(db_session)
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())

    assert "A" not in outcome.summary.split()  # pas de lettre nue isolée
    assert "représentent" in outcome.summary
    assert "3" in outcome.summary


def test_syn_j_annual_value_is_within_tolerance_of_the_injected_value(db_session):
    result = syn.build_syn_j(db_session)
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())
    par_id = {it.ingredient_id: it for it in outcome.items}

    for gros in result.gros:
        valeur = par_id[gros.id].annual_value
        assert abs(valeur - 250.0) / 250.0 < 0.05, f"{gros.name} : {valeur:.2f} € hors tolérance de 5%"


# ==========================================================================
# AC-F10-2 — historique insuffisant, jamais classé C par défaut
# ==========================================================================

def test_ac_f10_2_insufficient_history_is_not_determined_never_defaults_to_c(db_session):
    syn.build_syn_j(db_session)  # fournit un historique riche pour comparaison
    ing_recent = syn.ingredient(db_session, "Ingrédient tout juste ajouté", unit_cost=0.01)
    plat = syn.dish(db_session, "Plat récent", {ing_recent.id: 100.0})
    debut = datetime(2026, 10, 25)  # 1 semaine seulement avant le "as_of" ci-dessous
    syn.import_sales_rows(
        db_session, [(debut + timedelta(days=d), plat.name, 5.0, None) for d in range(7)],
        filename="recent.csv",
    )
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())

    par_id = {it.ingredient_id: it for it in outcome.items}
    item = par_id[ing_recent.id]
    assert item.computed_class is None
    assert item.effective_class is None
    assert "non déterminé" in item.explanation


def test_ac_f10_2_dormant_ingredient_is_flagged_not_a(db_session):
    """TC-F10-02 : un ingrédient à forte valeur historique mais sans aucune
    consommation depuis 3 semaines -> "dormant", jamais classé A."""
    result = syn.build_syn_j(db_session)
    ing = result.gros[0]
    as_of = datetime(2026, 11, 1).date()

    # Neutralise toute vente des 21 derniers jours avant `as_of` pour cet
    # ingrédient, sans toucher à son historique antérieur (qui reste riche).
    plat = db_session.query(models.Dish).filter(models.Dish.name.like(f"Plat {ing.name}%")).one()
    recent_cutoff = datetime.combine(as_of - timedelta(days=21), datetime.min.time())
    lignes_recentes = (
        db_session.query(models.SaleLine)
        .filter(models.SaleLine.dish_id == plat.id, models.SaleLine.sale_date > recent_cutoff)
        .all()
    )
    assert lignes_recentes, "le jeu doit contenir des ventes dans la fenêtre récente pour que le test prouve quelque chose"
    for ligne in lignes_recentes:
        ligne.quantity_sold = 0.0
    db_session.commit()
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=as_of)

    par_id = {it.ingredient_id: it for it in outcome.items}
    item = par_id[ing.id]
    assert item.computed_class == "dormant"
    assert item.effective_class == "dormant"
    assert "dormant" in item.explanation.lower()


# ==========================================================================
# AC-F10-3 — le forçage manuel prime et survit à un recalcul
# ==========================================================================

def test_ac_f10_3_manual_override_wins_and_survives_recalculation(db_session):
    result = syn.build_syn_j(db_session)
    petit = result.petits_small[0]  # class attendue : B ou C, jamais A sans forçage
    _enable_f10(db_session)

    ai_criticality.set_manual_override(db_session, petit.id, "A")
    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())
    item = next(it for it in outcome.items if it.ingredient_id == petit.id)

    assert item.manual_override == "A"
    assert item.effective_class == "A"
    assert item.computed_class != "A", "le calcul lui-même ne doit pas avoir changé, seul l'effectif"

    # "Survit à un recalcul" : un second appel à classify_ingredients (donc
    # un nouveau calcul complet, pas une valeur mise en cache) doit encore
    # refléter le forçage.
    outcome2 = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())
    item2 = next(it for it in outcome2.items if it.ingredient_id == petit.id)
    assert item2.effective_class == "A"


def test_set_manual_override_rejects_invalid_class(db_session):
    result = syn.build_syn_j(db_session)
    with pytest.raises(ValueError):
        ai_criticality.set_manual_override(db_session, result.gros[0].id, "Z")


def test_manual_override_can_be_cleared(db_session):
    result = syn.build_syn_j(db_session)
    ai_criticality.set_manual_override(db_session, result.gros[0].id, "C")
    ai_criticality.set_manual_override(db_session, result.gros[0].id, None)
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())
    item = next(it for it in outcome.items if it.ingredient_id == result.gros[0].id)
    assert item.manual_override is None
    assert item.effective_class == item.computed_class


# ==========================================================================
# Volatilité — calculée et exposée, jamais utilisée pour reclasser seule
# ==========================================================================

def test_volatility_is_exposed_but_never_auto_promotes_a_class(db_session):
    """Point documenté comme volontairement non construit (ai_criticality.py,
    en-tête) : le document demande qu'un ingrédient "très volatil" de classe
    B remonte en A, mais ne fixe aucun seuil numérique. Ce test verrouille
    l'absence de cette promotion automatique tant que le seuil n'est pas
    tranché — s'il se met à échouer, c'est qu'un seuil a été ajouté sans
    mettre à jour ce test ni le documenter comme une décision actée."""
    result = syn.build_syn_j(db_session)
    petit = result.petits_small[0]
    base = datetime(2026, 9, 7)
    # Écarts extrêmement volatils (alternance +/-) sur l'historique de ce
    # petit ingrédient, sans toucher à sa valeur annuelle (donc sans le
    # faire remonter par le seul mécanisme de valeur).
    for i, ecart in enumerate([100.0, 900.0, 100.0, 900.0]):  # moyenne non nulle, CV eleve
        d = base + timedelta(days=(i + 1) * 7)
        session = syn.run_count_session(
            db_session, counted_by="Volatilité",
            counted={petit.id: petit.current_theoretical_stock - ecart},
            ended_at=d,
        )
    _enable_f10(db_session)

    outcome = ai_criticality.classify_ingredients(db_session, as_of=datetime(2026, 11, 1).date())
    item = next(it for it in outcome.items if it.ingredient_id == petit.id)

    assert item.volatility is not None, "le coefficient de variation doit être calculé (>= 3 comptages)"
    assert item.effective_class != "A", "aucune promotion automatique tant que le seuil n'est pas tranché"
