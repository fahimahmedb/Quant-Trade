"""ROB — robustesse sur données externes réelles (Lot IA-0,
docs/feature-plans/ia-f5-f9.md §3).

RÈGLE ABSOLUE (§3.1, à ne jamais enfreindre) : aucun résultat obtenu sur un
jeu externe ne peut déclencher, justifier ou calibrer une décision métier.
Ni activer une fonctionnalité IA, ni ajuster un seuil, ni servir
d'argument commercial. Ces tests prouvent que le code ne casse pas face à
de la donnée réelle et sale — rien de plus. Aucune assertion ci-dessous ne
porte sur la justesse d'une prévision ; seulement sur l'absence de crash,
de perte silencieuse de lignes, ou de valeur aberrante en sortie.

Jeux utilisés : les deux nommés à l'origine par le document (§3.3).

- `matthieugimbert/french-bakery-daily-sales` (« Bakery sales.csv »),
  licence Kaggle **`copyright-authors`** (tous droits réservés par l'auteur).
- `sulmansarwar/transactions-from-a-bakery` (« BreadBasket_DMS.csv »),
  licence Kaggle **`unknown`**.

Ni l'une ni l'autre n'autorise clairement l'usage envisagé au sens de la
règle §3.3 du document — vérifié via l'API Kaggle (voir `_log_license`,
appelée à chaque exécution). **Utilisés malgré ça sur instruction directe
et explicite du porteur du projet**, qui a retiré cette règle de
vérification pour ces deux jeux précis en connaissance de cause (le
risque avait été rapporté en détail avant l'instruction — voir
docs/bilan-ia-0.md). Cette dérogation ne couvre que la règle §3.3
(vérification de licence) ; la règle §3.1 ci-dessus reste entière et n'a
jamais été visée par l'instruction. Aucune donnée n'est commitée ni
redistribuée : téléchargée à chaque exécution dans un répertoire
temporaire pytest, jamais persistée dans le dépôt.

Optionnel par construction : nécessite le CLI `kaggle` (`pip install
kaggle`) et des identifiants valides (`~/.kaggle/access_token` ou
`kaggle.json`). Absents -> module ignoré proprement, jamais un échec — un
développeur sans compte Kaggle doit pouvoir lancer `pytest tests/` sans que
ROB ne bloque quoi que ce soit (ROB ne débloque aucun gate, tableau §0 du
document : ce n'est qu'un durcissement optionnel).
"""
import csv
import io
import itertools
import json
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

import pytest

from app import models
from app.services import ai_forecast, recipes, sales_import, settings_service

KAGGLE_BIN = shutil.which("kaggle")

FRENCH_SLUG = "matthieugimbert/french-bakery-daily-sales"
FRENCH_FILE = "Bakery sales.csv"
BREADBASKET_SLUG = "sulmansarwar/transactions-from-a-bakery"
BREADBASKET_FILE = "BreadBasket_DMS.csv"


def _kaggle_configured() -> bool:
    if KAGGLE_BIN is None:
        return False
    return (Path.home() / ".kaggle" / "access_token").exists() or (Path.home() / ".kaggle" / "kaggle.json").exists()


def _log_license(out_dir: Path, slug: str) -> str:
    """Récupère et journalise la licence actuelle (jamais un gate ici — la
    vérification qui bloquait sur une licence non conforme a été retirée
    sur instruction explicite pour ces deux jeux, cf. docstring du module).
    Toujours ré-interrogée, jamais mise en cache, pour que le rapport de
    test reflète l'état réel de la licence au moment de l'exécution."""
    meta = subprocess.run(
        [KAGGLE_BIN, "datasets", "metadata", "-p", str(out_dir), slug],
        capture_output=True, text=True, timeout=30,
    )
    assert meta.returncode == 0, f"Échec de récupération des métadonnées Kaggle pour {slug} : {meta.stderr}"
    metadata = json.loads((out_dir / "dataset-metadata.json").read_text())
    licenses = metadata.get("info", {}).get("licenses") or []
    return licenses[0]["name"] if licenses else "inconnue"


def _download(out_dir: Path, slug: str, filename: str) -> Path:
    dl = subprocess.run(
        [KAGGLE_BIN, "datasets", "download", "-p", str(out_dir), "--force", slug],
        capture_output=True, text=True, timeout=120,
    )
    assert dl.returncode == 0, f"Échec du téléchargement Kaggle pour {slug} : {dl.stderr}"
    path = out_dir / filename
    if not path.exists():
        zips = list(out_dir.glob("*.zip"))
        assert zips, f"Aucun fichier ni archive trouvé pour {slug} dans {out_dir}"
        with zipfile.ZipFile(zips[0]) as z:
            z.extractall(out_dir)
    assert path.exists(), f"{filename} introuvable après téléchargement de {slug} dans {out_dir}"
    return path


@pytest.fixture(scope="module")
def french_bakery_csv_path(tmp_path_factory):
    if not _kaggle_configured():
        pytest.skip(
            "kaggle CLI ou identifiants absents (~/.kaggle/access_token ou kaggle.json) : "
            "ROB ignoré, optionnel par construction (docs/feature-plans/ia-f5-f9.md §3)."
        )
    out_dir = tmp_path_factory.mktemp("rob_french")
    license_name = _log_license(out_dir, FRENCH_SLUG)
    print(f"\nROB : licence actuelle de {FRENCH_SLUG} = {license_name!r} (utilisé malgré tout, cf. docstring)")
    return _download(out_dir, FRENCH_SLUG, FRENCH_FILE)


@pytest.fixture(scope="module")
def bread_basket_csv_path(tmp_path_factory):
    if not _kaggle_configured():
        pytest.skip(
            "kaggle CLI ou identifiants absents (~/.kaggle/access_token ou kaggle.json) : "
            "ROB ignoré, optionnel par construction (docs/feature-plans/ia-f5-f9.md §3)."
        )
    out_dir = tmp_path_factory.mktemp("rob_breadbasket")
    license_name = _log_license(out_dir, BREADBASKET_SLUG)
    print(f"\nROB : licence actuelle de {BREADBASKET_SLUG} = {license_name!r} (utilisé malgré tout, cf. docstring)")
    return _download(out_dir, BREADBASKET_SLUG, BREADBASKET_FILE)


def _adapt_french_bakery(raw_path: Path, limit: int | None = None) -> tuple[str, int]:
    """Reformate l'export réel (colonnes `,date,time,ticket_number,article,
    Quantity,unit_price`) vers ce que le parseur de l'app reconnaît
    (`date,plat,quantite,prix_unitaire`). Seuls les noms de colonnes sont
    normalisés — `date` est déjà au format ISO, aucune retouche. Le prix
    est transmis TEL QUEL (« 0,90 € », virgule décimale + symbole monétaire
    français) : c'est justement le format réel que ROB doit faire atteindre
    au parseur, pas une version pré-nettoyée qui ne prouverait rien sur son
    comportement réel face à ce format (voir ROB-02 : `unit_price` finit à
    None sur toutes les lignes, silencieusement — le symbole « € » fait
    échouer le float() du parseur après le remplacement virgule->point,
    caractérisé ici plutôt que corrigé en douce)."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "plat", "quantite", "prix_unitaire"])
    row_count = 0
    with raw_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = itertools.islice(reader, limit) if limit else reader
        for row in rows:
            writer.writerow([row.get("date", ""), row.get("article", ""), row.get("Quantity", ""), row.get("unit_price", "")])
            row_count += 1
    return out.getvalue(), row_count


def _adapt_bread_basket(raw_path: Path) -> tuple[str, int]:
    """Reformate l'export réel (colonnes `Date,Time,Transaction,Item`, une
    ligne par article vendu) vers `date,plat,quantite` — quantité 1 par
    ligne car ce jeu est au niveau article, pas agrégé par jour. La saleté
    qui intéresse ROB-03 (doublons, lignes "NONE"/"Adjustment") n'est
    JAMAIS filtrée ici : elle doit atteindre le parseur telle quelle."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "plat", "quantite"])
    row_count = 0
    with raw_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            writer.writerow([row.get("Date", ""), row.get("Item", ""), "1"])
            row_count += 1
    return out.getvalue(), row_count


# ==========================================================================
# ROB-01 — le parseur ne plante pas, rapport de lignes non interprétées cohérent
# ==========================================================================

def test_rob_01_import_never_raises_and_reports_cleanly(french_bakery_csv_path, seeded_client):
    content, row_count = _adapt_french_bakery(french_bakery_csv_path, limit=10_000)
    with seeded_client.session_factory() as db:
        sales_import_obj, parsed = sales_import.import_sales(db, "rob_french.csv", content)

    assert sales_import_obj.row_count == row_count
    # Aucun plat de ce jeu externe ("BAGUETTE", "CROISSANT"...) ne correspond
    # au menu du restaurant seedé (jeu de démo totalement différent) : tout
    # doit être signalé "non apparié" proprement, jamais planter.
    assert sales_import_obj.unmatched_count == row_count
    assert parsed.errors == [] or all(isinstance(e, str) for e in parsed.errors)


# ==========================================================================
# ROB-02 — texte français réel non corrompu ; format de prix réel caractérisé
# ==========================================================================

def test_rob_02_french_article_names_survive_the_round_trip(french_bakery_csv_path, seeded_client):
    content, _ = _adapt_french_bakery(french_bakery_csv_path, limit=10_000)
    with seeded_client.session_factory() as db:
        sales_import_obj, _ = sales_import.import_sales(db, "rob_french_texte.csv", content)
        noms = {
            line.raw_dish_name
            for line in db.query(models.SaleLine)
            .filter(models.SaleLine.sales_import_id == sales_import_obj.id)
            .all()
        }
    attendus = {"BAGUETTE", "PAIN AU CHOCOLAT", "TRADITIONAL BAGUETTE"}
    assert attendus & noms, "aucun des noms de produits français attendus n'a survécu à l'import"
    assert "�" not in "".join(noms), "caractère de remplacement Unicode détecté : encodage corrompu"


def test_rob_02_french_currency_price_format_is_characterized_not_silently_wrong(french_bakery_csv_path, seeded_client):
    """Caractérise un vrai défaut de tolérance du parseur plutôt que de le
    cacher : `unit_price` (règle française "0,90 €") ne matche aucun des
    formats que `_parse_row`/`float()` accepte après le remplacement
    virgule -> point ("0.90 €" n'est pas un float valide, le symbole
    monétaire reste). Résultat actuel : prix silencieusement absent
    (`unit_price=None`), jamais une exception ni une ligne rejetée — no
    crash, mais pas un signalement explicite non plus. Documenté ici comme
    piste d'amélioration future du parseur, pas corrigé dans ce lot (hors
    périmètre F5/F6/F7/F9)."""
    content, _ = _adapt_french_bakery(french_bakery_csv_path, limit=10_000)
    with seeded_client.session_factory() as db:
        sales_import_obj, _ = sales_import.import_sales(db, "rob_french_prix.csv", content)
        prix_recuperes = [
            line.unit_price
            for line in db.query(models.SaleLine)
            .filter(models.SaleLine.sales_import_id == sales_import_obj.id)
            .limit(100)
            .all()
        ]
    assert all(p is None for p in prix_recuperes), (
        "le format « X,XX € » est maintenant accepté quelque part dans le pipeline — "
        "si ce test échoue, la caractérisation ci-dessus (documentée aussi dans le "
        "commit) est devenue fausse, à mettre à jour plutôt qu'à contourner"
    )


# ==========================================================================
# ROB-03 — doublons et lignes hors-menu ("NONE", "Adjustment") : traçables, jamais fusionnés
# ==========================================================================

def test_rob_03_duplicate_and_off_menu_rows_are_each_individually_preserved(bread_basket_csv_path, seeded_client):
    """Le contrôle ACTIF de doublons (avertir l'utilisateur avant import)
    est le rôle de F15 (extension F10-F19, hors périmètre de ce lot) — pas
    encore construit. Ce que ce test prouve à la place, sur les vraies
    lignes dupliquées et les vraies lignes hors-menu de ce jeu ("NONE",
    "Adjustment") : rien n'est fusionné, dédupliqué ou perdu silencieusement
    pendant l'import — chaque ligne d'entrée produit sa propre ligne de
    vente, retrouvable."""
    content, row_count = _adapt_bread_basket(bread_basket_csv_path)
    with seeded_client.session_factory() as db:
        sales_import_obj, _ = sales_import.import_sales(db, "rob_breadbasket.csv", content)
        total_lignes = (
            db.query(models.SaleLine)
            .filter(models.SaleLine.sales_import_id == sales_import_obj.id)
            .count()
        )
        lignes_none = (
            db.query(models.SaleLine)
            .filter(
                models.SaleLine.sales_import_id == sales_import_obj.id,
                models.SaleLine.raw_dish_name == "NONE",
            )
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
    assert lignes_none >= 1, "les lignes hors-menu réelles 'NONE' du jeu externe doivent rester traçables"
    assert lignes_adjustment >= 1, "la ligne hors-menu réelle 'Adjustment' du jeu externe doit rester traçable"


# ==========================================================================
# ROB-04 — pipeline complet sur volume réel, temps mesuré et journalisé
# ==========================================================================

def test_rob_04_full_pipeline_completes_in_bounded_time_on_real_volume(french_bakery_csv_path, seeded_client):
    content, row_count = _adapt_french_bakery(french_bakery_csv_path)  # sans limite : les ~234 000 lignes réelles
    assert row_count > 200_000, f"volume réel attendu proche des ~234 000 lignes du document, obtenu {row_count}"

    debut = time.monotonic()
    with seeded_client.session_factory() as db:
        sales_import_obj, _ = sales_import.import_sales(db, "rob_french_volume.csv", content)
    duree = time.monotonic() - debut

    print(f"\nROB-04 : {row_count} lignes importées en {duree:.1f}s ({row_count / duree:.0f} lignes/s)")
    assert sales_import_obj.row_count == row_count
    assert duree < 300.0, f"pipeline complet trop lent sur volume réel : {duree:.1f}s pour {row_count} lignes"


# ==========================================================================
# ROB-05 — aucune sortie aberrante des fonctionnalités IA sur données réelles
# ==========================================================================

def test_rob_05_f6_forecast_has_no_aberrant_values_on_real_data(french_bakery_csv_path, seeded_client):
    """F6 (mode ombre) tourne sur les vraies ventes du produit le plus
    fréquent de ce jeu ("BAGUETTE", cité par le document comme leader des
    ventes), relié à un ingrédient/plat créés pour l'occasion — aucune
    assertion sur la JUSTESSE de la prévision (interdit par la règle
    §3.1), seulement sur l'absence de NaN/infini/négatif."""
    with seeded_client.session_factory() as db:
        farine = models.Ingredient(
            name="Farine ROB", unit=models.Unit.UNITE, unit_cost=0.5,
            storage_zone=models.StorageZone.SEC, current_theoretical_stock=1_000_000.0,
        )
        db.add(farine)
        db.commit()
        # Le plat doit s'appeler exactement "BAGUETTE" pour apparier les
        # lignes réelles du jeu externe (résolution par nom exact du parseur).
        recipes.upsert_dish(
            db, dish_id=None, name="BAGUETTE", is_active=True,
            lines=[recipes.RecipeLineInput(ingredient_id=farine.id, quantity=1.0)],
        )
        # 60 000 lignes ~ plusieurs mois sur ce jeu (~370 lignes/jour en
        # moyenne) : largement au-dessus du gate F6 (>=6 semaines), pas
        # besoin des ~234 000 lignes complètes pour cette vérification.
        content, _ = _adapt_french_bakery(french_bakery_csv_path, limit=60_000)
        sales_import.import_sales(db, "rob_french_f6.csv", content)

        settings_service.get_settings(db)
        settings = db.get(models.Settings, 1)
        settings.feature_f6_enabled = True
        db.commit()

        outcome = ai_forecast.weekday_forecast(db, farine.id)

    if not outcome.gate_ok:
        pytest.skip(f"gate F6 non atteint sur ce sous-ensemble réel ({outcome.gate_message}) : rien à vérifier")

    for wd, qty in outcome.forecast.expected_daily_qty.items():
        assert qty == qty, f"NaN détecté pour le jour {wd}"  # NaN != NaN
        assert qty not in (float("inf"), float("-inf")), f"valeur infinie détectée pour le jour {wd}"
        assert qty >= 0, f"quantité négative détectée pour le jour {wd} : {qty}"
