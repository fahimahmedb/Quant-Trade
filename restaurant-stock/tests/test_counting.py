from app import models
from app.services import counting


def _ingredient(db_session, name, zone, stock):
    ing = models.Ingredient(
        name=name,
        unit=models.Unit.GRAMME,
        unit_cost=0.02,
        storage_zone=zone,
        current_theoretical_stock=stock,
    )
    db_session.add(ing)
    db_session.commit()
    return ing


def test_start_count_session_prefills_theoretical_stock_ordered_by_zone(db_session):
    frigo_item = _ingredient(db_session, "Crème", models.StorageZone.FRIGO_POSITIF, 2000)
    sec_item = _ingredient(db_session, "Riz", models.StorageZone.SEC, 5000)

    session = counting.start_count_session(db_session, counted_by="Marie")

    assert len(session.lines) == 2
    # Trié par zone : frigo_positif vient avant sec alphabétiquement.
    zones = [line.ingredient.storage_zone for line in session.lines]
    assert zones == sorted(zones, key=lambda z: z.value)
    line_by_ingredient = {line.ingredient_id: line for line in session.lines}
    assert line_by_ingredient[frigo_item.id].theoretical_quantity == 2000
    assert line_by_ingredient[sec_item.id].theoretical_quantity == 5000
    assert all(line.counted_quantity is None for line in session.lines)


def test_confirm_count_line_records_value_and_reason(db_session):
    ing = _ingredient(db_session, "Beurre", models.StorageZone.FRIGO_POSITIF, 1000)
    session = counting.start_count_session(db_session)
    line = session.lines[0]

    updated = counting.confirm_count_line(
        db_session, line.id, counted_quantity=900, variance_reason=models.VarianceReason.CASSE
    )

    assert updated.counted_quantity == 900
    assert updated.variance_reason == models.VarianceReason.CASSE
    assert updated.confirmed_at is not None
    assert updated.variance == 100  # théorique 1000 - réel 900
    assert updated.variance_value == 100 * ing.unit_cost


def test_complete_session_recalibrates_theoretical_stock(db_session):
    ing = _ingredient(db_session, "Farine", models.StorageZone.SEC, 10000)
    session = counting.start_count_session(db_session)
    line = session.lines[0]
    counting.confirm_count_line(db_session, line.id, counted_quantity=9500)

    completed = counting.complete_count_session(db_session, session.id)

    assert completed.is_completed
    assert completed.duration_seconds is not None
    db_session.refresh(ing)
    assert ing.current_theoretical_stock == 9500
    movement = (
        db_session.query(models.StockMovement)
        .filter(models.StockMovement.movement_type == models.MovementType.COMPTAGE)
        .one()
    )
    assert movement.quantity_delta == -500
    assert movement.resulting_stock == 9500


def test_complete_session_skips_lines_never_counted(db_session):
    _ingredient(db_session, "Sel", models.StorageZone.SEC, 100)
    session = counting.start_count_session(db_session)
    # Aucune ligne confirmée : ne doit pas planter ni créer de mouvement.
    completed = counting.complete_count_session(db_session, session.id)
    assert completed.is_completed
    assert db_session.query(models.StockMovement).count() == 0


def test_variance_report_sorted_by_absolute_value_desc(db_session):
    small = _ingredient(db_session, "Poivre", models.StorageZone.SEC, 100)
    small.unit_cost = 0.05
    big = _ingredient(db_session, "Boeuf", models.StorageZone.FRIGO_POSITIF, 5000)
    big.unit_cost = 0.03
    db_session.commit()

    session = counting.start_count_session(db_session)
    lines_by_ing = {line.ingredient_id: line for line in session.lines}
    # Petit écart en valeur : 5 * 0.05 = 0.25 €
    counting.confirm_count_line(db_session, lines_by_ing[small.id].id, counted_quantity=95)
    # Gros écart en valeur : 500 * 0.03 = 15 €
    counting.confirm_count_line(db_session, lines_by_ing[big.id].id, counted_quantity=4500)

    report = counting.variance_report(db_session, session.id)

    assert [line.ingredient_id for line in report] == [big.id, small.id]
