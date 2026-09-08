"""ROB — robustesse sur données externes réelles (Lot IA-0,
docs/IA scope.md §3).

RÈGLE ABSOLUE (§3.1, à ne jamais enfreindre) : aucun résultat obtenu sur un
jeu externe ne peut déclencher, justifier ou calibrer une décision métier.
Ni activer une fonctionnalité IA, ni ajuster un seuil, ni servir
d'argument commercial. Ces tests prouvent que le code ne casse pas face à
de la donnée réelle et sale — rien de plus. Aucune assertion ci-dessous ne
porte sur la justesse d'une prévision ; seulement sur l'absence de crash,
de perte silencieuse de lignes, ou de valeur aberrante en sortie.

Jeu utilisé : `akashdeepkuila/bakery` (fichier `Bakery.csv`, licence
CC0-1.0, vérifiée par ce module à chaque exécution — voir
`_verify_license`). PAS les deux jeux nommés à l'origine par le document
(« French bakery daily sales » et « Transactions from a bakery ») : leurs
licences Kaggle réelles (« unknown » et « copyright-authors »)
n'autorisent pas clairement cet usage, vérifié via l'API Kaggle — détaillé
dans docs/bilan-ia-0.md. Ce remplaçant couvre le même type de saleté
(doublons, lignes hors-menu « Adjustment ») que le jeu original visait,
mais en anglais, pas en français : aucun jeu externe de vente/restauration
sous licence claire et de taille suffisante en français n'a été trouvé —
limite documentée plutôt qu'ignorée (docs/bilan-ia-0.md). Le volume réel
(~20 500 lignes) est aussi plus petit que les ~234 000 lignes du document ;
ROB-04 mesure et journalise le temps réel plutôt que de prétendre à un
volume qu'aucun jeu sous licence compatible n'offrait.

Optionnel par construction : nécessite le CLI `kaggle` (`pip install
kaggle`) et des identifiants valides (`~/.kaggle/access_token` ou
`kaggle.json`). Absents -> module ignoré proprement, jamais un échec — un
développeur sans compte Kaggle doit pouvoir lancer `pytest tests/` sans que
ROB ne bloque quoi que ce soit (ROB ne débloque aucun gate, tableau §0 du
document : ce n'est qu'un durcissement optionnel).
"""
import csv
import io
import json
import shutil
import subprocess
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

from app import models
from app.services import ai_forecast, sales_import, settings_service

KAGGLE_BIN = shutil.which("kaggle")
DATASET_SLUG = "akashdeepkuila/bakery"
DATASET_FILE = "Bakery.csv"
EXPECTED_LICENSE = "CC0-1.0"


def _kaggle_configured() -> bool:
    if KAGGLE_BIN is None:
        return False
    return (Path.home() / ".kaggle" / "access_token").exists() or (Path.home() / ".kaggle" / "kaggle.json").exists()


@pytest.fixture(scope="module")
def bakery_csv_path(tmp_path_factory):
    if not _kaggle_configured():
        pytest.skip(
            "kaggle CLI ou identifiants absents (~/.kaggle/access_token ou kaggle.json) : "
            "ROB ignoré, optionnel par construction (docs/IA scope.md §3)."
        )
    out_dir = tmp_path_factory.mktemp("rob_bakery")

    meta = subprocess.run(
        [KAGGLE_BIN, "datasets", "metadata", "-p", str(out_dir), DATASET_SLUG],
        capture_output=True, text=True, timeout=30,
    )
    assert meta.returncode == 0, f"Échec de récupération des métadonnées Kaggle : {meta.stderr}"
    metadata = json.loads((out_dir / "dataset-metadata.json").read_text())
    licenses = metadata.get("info", {}).get("licenses") or []
    license_name = licenses[0]["name"] if licenses else "inconnue"
    # Re-vérifiée à CHAQUE exécution, pas une fois pour toutes : un jeu peut
    # changer de licence après coup (règle §3.1 — ne jamais utiliser sans
    # autorisation claire, y compris si elle a changé depuis la dernière fois).
    if license_name != EXPECTED_LICENSE:
        pytest.fail(
            f"Licence de {DATASET_SLUG} passée de {EXPECTED_LICENSE!r} à {license_name!r} "
            "depuis la dernière vérification : re-confirmer avant de continuer à utiliser ce "
            "jeu (règle absolue, docs/IA scope.md §3.1) — ROB volontairement arrêté plutôt que "
            "de continuer sur une licence non revérifiée."
        )

    dl = subprocess.run(
        [KAGGLE_BIN, "datasets", "download", "-p", str(out_dir), "-f", DATASET_FILE, "--force", DATASET_SLUG],
        capture_output=True, text=True, timeout=60,
    )
    assert dl.returncode == 0, f"Échec du téléchargement Kaggle : {dl.stderr}"

    csv_path = out_dir / DATASET_FILE
    if not csv_path.exists():
        zip_path = out_dir / f"{DATASET_FILE}.zip"
        if zip_path.exists():
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(out_dir)
    assert csv_path.exists(), f"{DATASET_FILE} introuvable après téléchargement dans {out_dir}"
    return csv_path


def _adapt_to_app_csv(raw_path: Path) -> tuple[str, int]:
    """Reformate l'export réel (colonnes `TransactionNo,Items,DateTime,
    Daypart,DayType`, une ligne par article vendu) vers ce que le parseur
    de l'app reconnaît (`date,plat,quantite`) — l'étape d'intégration
    qu'exigerait ce logiciel de caisse précis en production (chaque caisse
    a ses propres intitulés, cf. app/services/sales_import.py). Seuls le
    nom des colonnes et le format de date (l'heure est retirée : le
    parseur n'accepte que des dates pures) sont normalisés — la quantité
    vaut 1 par ligne car ce jeu est au niveau article, pas agrégé par jour.
    La saleté qui intéresse ROB (doublons, lignes "Adjustment") n'est
    JAMAIS filtrée ici : elle doit atteindre le parseur telle quelle."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "plat", "quantite"])
    row_count = 0
    with raw_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            raw_date = row.get("DateTime", "") or ""
            date_part = raw_date.split(" ")[0]
            writer.writerow([date_part, row.get("Items", ""), "1"])
            row_count += 1
    return out.getvalue(), row_count


# ==========================================================================
# ROB-01 — le parseur ne plante pas, rapport de lignes non interprétées cohérent
# ==========================================================================

def test_rob_01_import_never_raises_and_reports_cleanly(bakery_csv_path, seeded_client):
    content, row_count = _adapt_to_app_csv(bakery_csv_path)
    with seeded_client.session_factory() as db:
        sales_import_obj, parsed = sales_import.import_sales(db, "rob_bakery.csv", content)

    assert sales_import_obj.row_count == row_count
    # Aucun plat de ce jeu externe ne correspond au menu du restaurant
    # seedé (jeu de démo totalement différent) : tout doit être signalé
    # "non apparié" proprement, jamais planter ni disparaître silencieusement.
    assert sales_import_obj.unmatched_count == row_count


# ==========================================================================
# ROB-02 — texte réel (accents/apostrophes/caractères spéciaux) non corrompu
# ==========================================================================

def test_rob_02_special_characters_in_item_names_survive_the_round_trip(bakery_csv_path, seeded_client):
    """Ce jeu de remplacement est anglophone (aucun jeu externe sous
    licence claire et de taille suffisante en français n'a été trouvé,
    cf. docs/bilan-ia-0.md) : ce test vérifie l'absence de corruption
    d'encodage sur les caractères spéciaux réellement présents (apostrophes,
    esperluettes, tirets) plutôt que des accents français spécifiquement —
    limite documentée, pas simulée."""
    content, _ = _adapt_to_app_csv(bakery_csv_path)
    with seeded_client.session_factory() as db:
        sales_import_obj, _ = sales_import.import_sales(db, "rob_bakery_texte.csv", content)
        noms = {
            line.raw_dish_name
            for line in db.query(models.SaleLine)
            .filter(models.SaleLine.sales_import_id == sales_import_obj.id)
            .all()
        }
    attendus_presents = {"Ella's Kitchen Pouches", "My-5 Fruit Shoot", "Cherry me Dried fruit"}
    assert attendus_presents & noms, "aucun des noms à caractères spéciaux attendus n'a survécu à l'import"
    assert "�" not in "".join(noms), "caractère de remplacement Unicode détecté : encodage corrompu"


# ==========================================================================
# ROB-03 — doublons et lignes hors-menu : traçables individuellement, jamais fusionnés
# ==========================================================================

def test_rob_03_duplicate_and_off_menu_rows_are_each_individually_preserved(bakery_csv_path, seeded_client):
    """Le contrôle ACTIF de doublons (avertir l'utilisateur avant import)
    est le rôle de F15 (extension F10-F19, hors périmètre de ce lot) — pas
    encore construit. Ce que ce test prouve à la place, sur les vraies
    lignes dupliquées et la vraie ligne "Adjustment" de ce jeu : rien n'est
    fusionné, dédupliqué ou perdu silencieusement pendant l'import — chaque
    ligne d'entrée produit sa propre ligne de vente, retrouvable."""
    content, row_count = _adapt_to_app_csv(bakery_csv_path)
    with seeded_client.session_factory() as db:
        sales_import_obj, _ = sales_import.import_sales(db, "rob_bakery_doublons.csv", content)
        total_lignes = (
            db.query(models.SaleLine)
            .filter(models.SaleLine.sales_import_id == sales_import_obj.id)
            .count()
        )
        lignes_adjustment = (
            db.query(models.SaleLine)
            .filter(
                models.SaleLine.sales_import_id == sales_import_obj.id,
                models.SaleLine.raw_dish_name == "Adjustment",
            )
            .count()
        )
    assert total_lignes == row_count, "des lignes ont disparu pendant l'import (fusion ou perte silencieuse)"
    assert lignes_adjustment >= 1, "la ligne hors-menu réelle 'Adjustment' du jeu externe doit rester traçable"


# ==========================================================================
# ROB-04 — pipeline complet sur volume réel, temps mesuré et journalisé
# ==========================================================================

def test_rob_04_full_pipeline_completes_in_bounded_time_on_real_volume(bakery_csv_path, seeded_client, capsys):
    content, row_count = _adapt_to_app_csv(bakery_csv_path)
    assert row_count > 15_000, "volume réel attendu de l'ordre de la dizaine de milliers de lignes"

    debut = time.monotonic()
    with seeded_client.session_factory() as db:
        sales_import_obj, _ = sales_import.import_sales(db, "rob_bakery_volume.csv", content)
    duree = time.monotonic() - debut

    print(f"ROB-04 : {row_count} lignes importées en {duree:.2f}s ({row_count / duree:.0f} lignes/s)")
    assert sales_import_obj.row_count == row_count
    assert duree < 30.0, f"pipeline complet trop lent sur volume réel : {duree:.2f}s pour {row_count} lignes"


# ==========================================================================
# ROB-05 — aucune sortie aberrante des fonctionnalités IA sur données réelles
# ==========================================================================

def test_rob_05_f6_forecast_has_no_aberrant_values_on_real_data(bakery_csv_path, seeded_client):
    """F6 (mode ombre) tourne sur les vraies ventes de l'article le plus
    fréquent de ce jeu ("Bread"), relié à un ingrédient/plat créés pour
    l'occasion — aucune assertion sur la JUSTESSE de la prévision (interdit
    par la règle §3.1), seulement sur l'absence de NaN/infini/négatif."""
    content, _ = _adapt_to_app_csv(bakery_csv_path)
    with seeded_client.session_factory() as db:
        pain = models.Ingredient(
            name="Pain ROB", unit=models.Unit.UNITE, unit_cost=0.5,
            storage_zone=models.StorageZone.SEC, current_theoretical_stock=100_000.0,
        )
        db.add(pain)
        db.commit()
        # Le plat doit s'appeler exactement "Bread" pour apparier les
        # lignes réelles du jeu externe (résolution par nom exact du parseur).
        from app.services import recipes
        plat = recipes.upsert_dish(
            db, dish_id=None, name="Bread", is_active=True,
            lines=[recipes.RecipeLineInput(ingredient_id=pain.id, quantity=1.0)],
        )
        sales_import.import_sales(db, "rob_bakery_f6.csv", content)

        settings_service.get_settings(db)
        settings = db.get(models.Settings, 1)
        settings.feature_f6_enabled = True
        db.commit()

        outcome = ai_forecast.weekday_forecast(db, pain.id)

    if not outcome.gate_ok:
        pytest.skip(f"gate F6 non atteint sur ce sous-ensemble réel ({outcome.gate_message}) : rien à vérifier")

    for wd, qty in outcome.forecast.expected_daily_qty.items():
        assert qty == qty, f"NaN détecté pour le jour {wd}"  # NaN != NaN
        assert qty not in (float("inf"), float("-inf")), f"valeur infinie détectée pour le jour {wd}"
        assert qty >= 0, f"quantité négative détectée pour le jour {wd} : {qty}"
