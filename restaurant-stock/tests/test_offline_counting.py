"""F3 — comptage hors-ligne (TC-F3-01 à TC-F3-05).

Le comptage se fait en réserve et en chambre froide, là où le réseau tombe.
Ces tests couvrent le contrat serveur de la file hors-ligne : ce qui est saisi
sans réseau doit arriver intact, et ce qui ne peut pas être appliqué doit être
dit, jamais fusionné en silence.
"""
import re
from datetime import datetime, timedelta

from app import models
from app.services import counting

EPOCH = datetime(1970, 1, 1)


def _ms(moment: datetime) -> int:
    """Horodatage en millisecondes epoch, comme l'envoie le navigateur."""
    return int((moment - EPOCH).total_seconds() * 1000)


def _start_session(client) -> int:
    response = client.post("/counting/start", data={"counted_by": "Marie"})
    assert response.status_code < 400
    return int(re.search(r"/counting/(\d+)", str(response.url)).group(1))


def _revision(client, session_id: int) -> str:
    """Empreinte telle que la page la porte — comme un appareil l'aurait lue."""
    html = client.get(f"/counting/{session_id}").text
    return re.search(r'data-count-revision="([^"]+)"', html).group(1)


def _lines_by_zone(db, session_id):
    session = db.get(models.CountSession, session_id)
    grouped = {}
    for line in session.lines:
        grouped.setdefault(line.ingredient.storage_zone, []).append(line)
    return grouped


# --------------------------------------------------------------------------
# TC-F3-01 — coupure réseau au milieu d'un comptage de 9 lignes.
# --------------------------------------------------------------------------
def test_tc_f3_01_offline_entries_reach_server_after_reconnect(seeded_client):
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)

    with factory() as db:
        grouped = _lines_by_zone(db, session_id)
        online_zones = [z for z in grouped if z != models.StorageZone.FRIGO_POSITIF]
        offline_lines = [(l.id, l.ingredient.name) for l in grouped[models.StorageZone.FRIGO_POSITIF]]
        online_payloads = [
            (zone, {f"count_{line.id}": "7" for line in grouped[zone]}) for zone in online_zones
        ]
        total_lines = sum(len(v) for v in grouped.values())

    assert total_lines == 9, "le jeu de démo doit donner 9 lignes à compter"
    assert len(offline_lines) == 5

    # 4 lignes saisies en ligne, avant la coupure.
    for zone, data in online_payloads:
        assert client.post(f"/counting/{session_id}/zone/{zone.value}", data=data).status_code < 400

    with factory() as db:
        counted = sum(1 for l in db.get(models.CountSession, session_id).lines
                      if l.counted_quantity is not None)
    assert counted == 4

    # Coupure : les 5 dernières lignes partent dans la file locale, puis sont
    # rejouées d'un bloc à la reconnexion.
    entered = datetime.utcnow() - timedelta(minutes=3)
    response = client.post(f"/counting/{session_id}/sync", json={
        "revision": _revision(client, session_id),
        "entries": [
            {"line_id": line_id, "counted_quantity": 123.5,
             "variance_reason": "", "entered_at": _ms(entered)}
            for line_id, _ in offline_lines
        ],
    })

    assert response.status_code == 200
    assert response.json()["applied"] == 5
    assert response.json()["unknown"] == []

    with factory() as db:
        lines = db.get(models.CountSession, session_id).lines
        assert all(l.counted_quantity is not None for l in lines), "ligne perdue à la reconnexion"
        assert len(lines) == 9
        for line_id, _ in offline_lines:
            assert db.get(models.CountLine, line_id).counted_quantity == 123.5


# --------------------------------------------------------------------------
# TC-F3-02 — brouillon repris : la saisie hors-ligne n'est pas perdue et la
# reprise ne réécrit pas par-dessus une valeur plus récente.
# --------------------------------------------------------------------------
def test_tc_f3_02_queued_draft_replayed_once_reconnected(seeded_client):
    """Volet serveur de la reprise de brouillon.

    Le stockage local est vérifié dans le test navigateur (test_offline_pwa) ;
    ici on vérifie que rejouer une file, même deux fois, donne le bon état.
    """
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)
    with factory() as db:
        line = db.get(models.CountSession, session_id).lines[0]
        line_id = line.id

    entered = datetime.utcnow() - timedelta(minutes=10)
    queue = [{"line_id": line_id, "counted_quantity": 42.0,
              "variance_reason": "casse", "entered_at": _ms(entered)}]

    first = client.post(f"/counting/{session_id}/sync", json={"entries": queue})
    assert first.json()["applied"] == 1

    # Onglet rouvert, file encore présente : rejouer ne doit rien casser.
    second = client.post(f"/counting/{session_id}/sync", json={"entries": queue})
    assert second.status_code == 200
    assert second.json()["conflicts"] == []

    with factory() as db:
        line = db.get(models.CountLine, line_id)
        assert line.counted_quantity == 42.0
        assert line.variance_reason == models.VarianceReason.CASSE
        # L'horodatage epoch-ms perd les microsecondes : à la milliseconde près.
        assert abs((line.confirmed_at - entered).total_seconds()) < 0.001


# --------------------------------------------------------------------------
# TC-F3-03 — deux appareils sur la même session.
# --------------------------------------------------------------------------
def test_tc_f3_03_two_devices_conflict_is_reported_and_no_line_lost(seeded_client):
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)
    with factory() as db:
        lines = sorted(db.get(models.CountSession, session_id).lines, key=lambda l: l.id)
        shared_id, shared_name = lines[0].id, lines[0].ingredient.name
        own_id = lines[1].id

    now = datetime.utcnow()
    # Appareil A, en ligne, saisit la ligne partagée il y a 2 minutes.
    client.post(f"/counting/{session_id}/sync", json={"entries": [
        {"line_id": shared_id, "counted_quantity": 500.0, "entered_at": _ms(now - timedelta(minutes=2))},
    ]})

    # Appareil B était hors-ligne : sa saisie de la même ligne est plus ancienne.
    response = client.post(f"/counting/{session_id}/sync", json={"entries": [
        {"line_id": shared_id, "counted_quantity": 999.0, "entered_at": _ms(now - timedelta(minutes=30))},
        {"line_id": own_id, "counted_quantity": 77.0, "entered_at": _ms(now - timedelta(minutes=29))},
    ]})

    body = response.json()
    assert body["applied"] == 1, "la ligne propre à B doit passer"
    assert len(body["conflicts"]) == 1
    conflict = body["conflicts"][0]
    assert conflict["ingredient"] == shared_name
    assert conflict["kept"] == 500.0 and conflict["discarded"] == 999.0

    with factory() as db:
        assert db.get(models.CountLine, shared_id).counted_quantity == 500.0
        assert db.get(models.CountLine, own_id).counted_quantity == 77.0


def test_tc_f3_03_newer_offline_entry_overwrites_older_server_value(seeded_client):
    """Le sens inverse : hors-ligne mais plus récent, la saisie l'emporte."""
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)
    with factory() as db:
        line_id = sorted(db.get(models.CountSession, session_id).lines, key=lambda l: l.id)[0].id

    now = datetime.utcnow()
    client.post(f"/counting/{session_id}/sync", json={"entries": [
        {"line_id": line_id, "counted_quantity": 500.0, "entered_at": _ms(now - timedelta(hours=2))},
    ]})
    response = client.post(f"/counting/{session_id}/sync", json={"entries": [
        {"line_id": line_id, "counted_quantity": 610.0, "entered_at": _ms(now - timedelta(minutes=5))},
    ]})

    assert response.json()["conflicts"] == []
    with factory() as db:
        assert db.get(models.CountLine, line_id).counted_quantity == 610.0


# --------------------------------------------------------------------------
# TC-F3-04 — hors-ligne 24 h puis reconnexion.
# --------------------------------------------------------------------------
def test_tc_f3_04_day_old_offline_session_syncs_with_truthful_duration(seeded_client):
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)

    now = datetime.utcnow()
    started = now - timedelta(hours=25)
    finished = started + timedelta(minutes=40)  # comptage réel : 40 min, hier
    with factory() as db:
        session = db.get(models.CountSession, session_id)
        session.started_at = started
        line_ids = [l.id for l in session.lines]
        db.commit()

    response = client.post(f"/counting/{session_id}/sync", json={
        "entries": [
            {"line_id": line_id, "counted_quantity": 10.0,
             "entered_at": _ms(started + timedelta(minutes=i + 1))}
            for i, line_id in enumerate(line_ids)
        ],
        "complete": True,
        "ended_at": _ms(finished),
    })

    body = response.json()
    assert response.status_code == 200
    assert body["applied"] == len(line_ids)
    assert body["completed"] is True

    with factory() as db:
        session = db.get(models.CountSession, session_id)
        assert session.is_completed
        # La durée est celle du comptage sur l'appareil, pas les 25 h écoulées
        # avant que le réseau revienne.
        assert 2350 < session.duration_seconds < 2450, session.duration_seconds
        # Le stock théorique a bien été recalé sur les valeurs saisies hier.
        assert all(l.ingredient.current_theoretical_stock == 10.0 for l in session.lines)


def test_tc_f3_04_absurd_client_clock_falls_back_to_server_time(seeded_client):
    """Téléphone à l'heure fausse : on préfère l'heure serveur à une saisie de 2037."""
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)
    with factory() as db:
        line_id = db.get(models.CountSession, session_id).lines[0].id

    response = client.post(f"/counting/{session_id}/sync", json={"entries": [
        {"line_id": line_id, "counted_quantity": 5.0, "entered_at": _ms(datetime(2037, 1, 1))},
    ]})

    assert response.json()["applied"] == 1
    with factory() as db:
        confirmed = db.get(models.CountLine, line_id).confirmed_at
        assert confirmed < datetime.utcnow() + timedelta(minutes=1)


# --------------------------------------------------------------------------
# TC-F3-05 — cache périmé.
# --------------------------------------------------------------------------
def test_tc_f3_05_stale_page_revision_is_reported_on_reconnect(seeded_client):
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)
    cached_revision = _revision(client, session_id)

    with factory() as db:
        session = db.get(models.CountSession, session_id)
        line_id = session.lines[0].id
        # Fiche renommée depuis un autre poste pendant que le téléphone comptait.
        ingredient = db.get(models.CountLine, line_id).ingredient
        ingredient.name = ingredient.name + " (bio)"
        db.commit()

    stale = client.post(f"/counting/{session_id}/sync", json={
        "revision": cached_revision,
        "entries": [{"line_id": line_id, "counted_quantity": 3.0}],
    })

    body = stale.json()
    assert body["stale"] is True, "une liste périmée doit être signalée"
    assert body["applied"] == 1, "la saisie reste enregistrée malgré la péremption"
    assert body["revision"] != cached_revision

    # Page rechargée : l'empreinte est à jour, plus d'alerte.
    fresh = client.post(f"/counting/{session_id}/sync", json={
        "revision": _revision(client, session_id),
        "entries": [{"line_id": line_id, "counted_quantity": 4.0}],
    })
    assert fresh.json()["stale"] is False


def test_tc_f3_05_unchanged_list_is_not_flagged_stale(seeded_client):
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)
    with factory() as db:
        line_id = db.get(models.CountSession, session_id).lines[0].id

    response = client.post(f"/counting/{session_id}/sync", json={
        "revision": _revision(client, session_id),
        "entries": [{"line_id": line_id, "counted_quantity": 1.0}],
    })
    assert response.json()["stale"] is False


def test_tc_f3_05_session_closed_elsewhere_refuses_queued_entries(seeded_client):
    """Session close depuis un autre appareil : on refuse d'écrire, on le dit.

    Le stock a déjà été recalé à la clôture ; appliquer des quantités après coup
    laisserait des lignes comptées sans mouvement de stock correspondant.
    """
    client, factory = seeded_client.client, seeded_client.session_factory
    session_id = _start_session(client)
    with factory() as db:
        line_id = db.get(models.CountSession, session_id).lines[0].id

    client.post(f"/counting/{session_id}/complete")

    response = client.post(f"/counting/{session_id}/sync", json={"entries": [
        {"line_id": line_id, "counted_quantity": 888.0},
    ]})

    assert response.status_code == 409
    body = response.json()
    assert body["closed"] is True
    assert "autre appareil" in body["error"]
    with factory() as db:
        assert db.get(models.CountLine, line_id).counted_quantity != 888.0


# --------------------------------------------------------------------------
# Contrat de service, indépendamment du transport HTTP.
# --------------------------------------------------------------------------
def test_apply_entries_ignores_unknown_line_ids(db_session):
    ing = models.Ingredient(name="Sel", unit=models.Unit.GRAMME, unit_cost=0.001,
                            storage_zone=models.StorageZone.SEC, current_theoretical_stock=500)
    db_session.add(ing)
    db_session.commit()
    session = counting.start_count_session(db_session)

    result = counting.apply_entries(db_session, session.id, [
        counting.CountEntry(line_id=session.lines[0].id, counted_quantity=480),
        counting.CountEntry(line_id=999_999, counted_quantity=1),
    ])

    assert result.applied == [session.lines[0].id]
    assert result.unknown == [999_999]


def test_session_revision_changes_with_the_displayed_list(db_session):
    ing = models.Ingredient(name="Beurre", unit=models.Unit.GRAMME, unit_cost=0.01,
                            storage_zone=models.StorageZone.FRIGO_POSITIF,
                            current_theoretical_stock=1000)
    db_session.add(ing)
    db_session.commit()
    session = counting.start_count_session(db_session)

    before = counting.session_revision(db_session, session.id)
    # Une quantité saisie ne périme pas la liste : seule la fiche compte.
    counting.apply_entries(db_session, session.id, [
        counting.CountEntry(line_id=session.lines[0].id, counted_quantity=900)
    ])
    assert counting.session_revision(db_session, session.id) == before

    ing.storage_zone = models.StorageZone.CAVE
    db_session.commit()
    assert counting.session_revision(db_session, session.id) != before
