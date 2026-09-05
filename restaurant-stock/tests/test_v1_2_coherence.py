"""V1.2 — cohérence relevée en relisant les sept captures du lot 4 côte à côte.

Chaque test ici correspond à un défaut concret pointé sur les captures, pas à
une intention générale : séparateurs de /variance rendus noirs et bord à bord
(classe fantôme `divide-filet`, couvert dans test_design_tokens.py), lignes à
0,00 € qui prennent autant de place qu'un vrai écart (AC-U6-1), bouton de
fichier natif resté en anglais, point décimal sur des champs éditables
(OBS-3/NR-18 ne peut structurellement pas le voir, cf. plus bas), et le
raccourci « (s) » laissé un peu partout sur les pluriels.
"""
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from app import models
from app.services import counting, ordering, settings_service
from app.templating import _decimal_fr, _qty, pluriel, templates

BASE_DIR = Path(__file__).resolve().parent.parent
GABARITS = sorted((BASE_DIR / "app" / "templates").rglob("*.html"))
ROUTEURS_ET_SERVICES = sorted((BASE_DIR / "app" / "routers").glob("*.py")) + sorted(
    (BASE_DIR / "app" / "services").glob("*.py")
)
SCRIPTS = sorted((BASE_DIR / "app" / "static").glob("*.js"))


# ==========================================================================
# AC-U6-1 — un ingrédient sans écart n'occupe plus une ligne complète.
# ==========================================================================
def _ligne(nom, variance_value, theorique=100.0, compte=100.0, pct=0.0, motif=None):
    return SimpleNamespace(
        ingredient=SimpleNamespace(name=nom, unit=SimpleNamespace(value="g")),
        variance_value=variance_value,
        theoretical_quantity=theorique,
        counted_quantity=compte,
        variance_pct=pct,
        variance_reason=motif,
    )


def _rendu(report):
    return templates.env.get_template("partials/variance_table.html").render(report=report)


def test_ac_u6_1_zero_variance_lines_are_collapsed_behind_a_count():
    lignes = [
        _ligne("Steak haché", 3.44, 4100, 3813, 7.0),
        _ligne("Farine", 0.0, 14400, 14400, 0.0),
        _ligne("Tomate", 0.0, 3220, 3220, 0.0),
        _ligne("Mozzarella", -0.25, 700, 728, -4.0),
    ]
    html = _rendu(lignes)
    avant_details = html.split("<details", 1)[0]

    assert "Steak haché" in avant_details, "un vrai écart doit rester dans la liste principale"
    assert "Mozzarella" in avant_details, "un surplus (écart négatif) reste un vrai écart, pas un conforme"
    assert "Farine" not in avant_details, "un ingrédient sans écart occupe encore une ligne pleine"
    assert "Tomate" not in avant_details
    assert "2 ingrédients conformes, sans écart" in html
    assert "Farine" in html and "Tomate" in html, "les ingrédients conformes doivent rester consultables (repliés)"


def test_ac_u6_1_singular_count_agrees_in_french():
    html = _rendu([_ligne("Steak haché", 3.44), _ligne("Farine", 0.0)])
    assert "1 ingrédient conforme, sans écart" in html
    assert "1 ingrédients" not in html and "1 ingrédient conformes" not in html


def test_ac_u6_1_all_lines_zero_still_shows_a_clear_message():
    html = _rendu([_ligne("Farine", 0.0), _ligne("Tomate", 0.0)])
    assert "Tous les ingrédients comptés sont conformes" in html
    assert "<ul" not in html.split("<details", 1)[0], "pas de liste principale vide à afficher"
    assert "2 ingrédients conformes, sans écart" in html


def test_ac_u6_1_no_lines_at_all_keeps_the_original_empty_message():
    html = _rendu([])
    assert "Aucune ligne comptée dans cette session." in html
    assert "<details" not in html


def test_ac_u6_1_no_variance_lines_present_hides_the_collapsed_section():
    html = _rendu([_ligne("Steak haché", 3.44)])
    assert "<details" not in html, "rien à replier si tout est en écart"


# ==========================================================================
# Filtre `decimal_fr` — la virgule française sur les champs éditables passés
# en `type=\"text\"` (OBS-3/NR-18 ne pouvait pas voir ce bug : `_visible_text`
# retire délibérément les attributs `value=`, cf. test plus bas).
# ==========================================================================
def test_decimal_fr_uses_comma_and_drops_trailing_zeros():
    assert _decimal_fr(20.0) == "20"
    assert _decimal_fr(10.5) == "10,5"
    assert _decimal_fr(0.0025) == "0,0025"
    assert _decimal_fr(15) == "15"


def test_decimal_fr_handles_empty_and_none():
    assert _decimal_fr(None) == ""
    assert _decimal_fr("") == ""


def test_decimal_fr_passes_raw_strings_through_unchanged():
    """Un formulaire ré-affiché après une erreur de validation transmet la
    saisie brute de la personne (`SimpleNamespace` dans les routeurs
    settings/ingredients) : virgule déjà là, ou même invalide — c'est
    justement ce qu'elle doit revoir, pas une valeur reformatée."""
    assert _decimal_fr("12,5") == "12,5"
    assert _decimal_fr("n'importe quoi") == "n'importe quoi"


def test_decimal_fr_min_decimals_pads_without_ever_truncating_real_precision():
    """Un prix affiche partout ailleurs dans l'app au moins 2 décimales
    (`euros`/`unit_price`/`line_price` : « 1,20 € »), mais `decimal_fr` sans
    argument retire tous les zéros de fin (1,20 -> « 1,2 »), une
    incohérence relevée sur /deliveries/new. `min_decimals` comble ce
    manque en complétant par des zéros, sans jamais couper une précision
    réelle déjà supérieure (0,0025 garde ses 4 décimales)."""
    assert _decimal_fr(1.2, 2) == "1,20"
    assert _decimal_fr(20.0, 2) == "20,00"
    assert _decimal_fr(0.0025, 2) == "0,0025"  # précision réelle jamais tronquée


# ==========================================================================
# Fonction `pluriel` — remplace le raccourci « (s) ».
# ==========================================================================
def test_pluriel_is_empty_only_at_exactly_one():
    assert pluriel(1) == ""
    assert pluriel(0) == "s"
    assert pluriel(2) == "s"
    assert pluriel(40) == "s"


def test_no_parenthesized_plural_shortcut_remains_anywhere():
    """Trouvé huit fois dans les gabarits et autant dans les routeurs/scripts
    au moment de l'audit : `ligne(s)`, `plat(s)`, `suggestion(s)`… Un grep
    ciblé plutôt qu'une liste figée de fichiers, pour que le prochain qui
    revient au raccourci se fasse arrêter ici plutôt qu'en capture d'écran."""
    motif = re.compile(r"\w\(s\)|\w\(es\)")
    for fichier in GABARITS + ROUTEURS_ET_SERVICES + SCRIPTS:
        texte = fichier.read_text()
        trouve = motif.search(texte)
        assert trouve is None, f"pluriel entre parenthèses « {trouve.group(0) if trouve else ''} » dans {fichier}"


def test_no_stray_space_before_a_comma_from_an_untrimmed_jinja_if():
    """Retrouvé sept fois en corrigeant les pluriels ci-dessus, une capture
    d'écran à la fois : `{{ x }}\\n  {% if y %}, z{% endif %}` laisse l'espace
    d'indentation Jinja atterrir avant la virgule à l'écran (« 13 lignes , 1
    plat… »), parfois avec une balise ouvrante entre les deux (`<span>, …`).
    `{%- if %}` (trim) l'absorbe. Plutôt que corriger au fil des prochaines
    captures, un motif générique : un `{% if …%}` en tête de ligne, dont le
    contenu (avec ou sans balise simple avant) commence par une virgule, sans
    le `-` qui le protège."""
    motif = re.compile(r"\n[ \t]*\{%\s*if\b[^%]*%\}\s*(?:<[a-zA-Z][^>]*>)?\s*,")
    for gabarit in GABARITS:
        trouve = motif.search(gabarit.read_text())
        assert trouve is None, f"`{{% if %}}` non trimmé avant une virgule dans {gabarit}"


# ==========================================================================
# Point décimal sur les champs éditables — OBS-3/NR-18 vérifie le texte
# affiché (`_visible_text` retire les balises ET leurs attributs), donc ne
# peut par construction pas voir un point dans un `value=\"…\"` : il faut lire
# le HTML brut, pas le texte visible.
# ==========================================================================
def test_only_the_two_known_screens_still_use_type_number(seeded_client):
    """`rolling_window_days` (jours entiers, jamais de décimale) et l'écran de
    comptage actif (sa propre validation, pas celle-ci) sont les deux seules
    exceptions assumées. Les six autres champs décimaux sont passés en texte
    pour que la virgule française s'affiche pour de vrai (Chromium n'affiche
    jamais de virgule sur un `type=\"number\"`, quel que soit `lang`)."""
    client = seeded_client.client
    client.post("/ingredients/new", data={
        "name": "Test coherence", "unit": "g", "unit_cost": "0,0123",
        "storage_zone": "sec", "current_theoretical_stock": "10",
    })
    with seeded_client.session_factory() as db:
        ingredient_id = db.query(models.Ingredient).filter_by(name="Test coherence").one().id

    for path in (
        "/settings",
        f"/ingredients/{ingredient_id}/edit",
        "/recipes/new",
        "/deliveries/new",
    ):
        page = client.get(path).text
        for m in re.finditer(r'<input\b[^>]*>', page):
            balise = m.group(0)
            if 'type="number"' in balise:
                assert 'name="rolling_window_days"' in balise, (
                    f"type=number inattendu sur {path} : {balise}"
                )


def test_settings_decimal_fields_display_french_comma_end_to_end(seeded_client):
    """Symptôme exact signalé : « 20.0 », « 10.0 », « 15.0 » sur /settings."""
    client = seeded_client.client
    client.post("/settings", data={
        "safety_days": "20,5", "target_days": "10", "rolling_window_days": "7",
        "price_alert_pct": "15",
    })
    page = client.get("/settings").text
    valeurs = re.findall(
        r'name="(?:safety_days|target_days|price_alert_pct)"\s+value="([^"]*)"', page
    )
    assert len(valeurs) == 3
    for v in valeurs:
        assert "." not in v, f"point décimal encore affiché dans un champ éditable : {v!r}"
    assert "20,5" in page


def test_ingredient_form_decimal_fields_display_french_comma(seeded_client):
    client = seeded_client.client
    client.post("/ingredients/new", data={
        "name": "Coût avec décimales", "unit": "g", "unit_cost": "0,0123",
        "storage_zone": "sec", "current_theoretical_stock": "12,5",
    })
    with seeded_client.session_factory() as db:
        ingredient_id = db.query(models.Ingredient).filter_by(name="Coût avec décimales").one().id
    page = client.get(f"/ingredients/{ingredient_id}/edit").text
    valeurs = re.findall(
        r'name="(?:unit_cost|current_theoretical_stock)"\s+value="([^"]*)"', page
    )
    assert len(valeurs) == 2
    for v in valeurs:
        assert "." not in v, f"point décimal encore affiché : {v!r}"
    assert "0,0123" in page


def test_delivery_form_prefilled_price_displays_french_comma(seeded_client):
    """Trouvé en relisant une capture de /deliveries/new : `1.2 €/kg` restait
    au point décimal malgré le passage en `type=\"text\"` et le filtre
    `decimal_fr`. Cause réelle : le routeur formatait déjà le prix en chaîne
    avant que le gabarit ne le voie (`_price_input_value`, un reliquat de
    l'ancien `<input type=\"number\">`) — `decimal_fr` reçoit alors une
    chaîne déjà faite et la laisse passer telle quelle, pensé pour une
    ressaisie après erreur, pas pour une valeur déjà mise en forme ailleurs.
    Le routeur doit fournir un nombre, pas une chaîne pré-formatée.

    Le prix pré-rempli ne vit plus dans `value=` de `unit_price` (aucun
    ingrédient n'est plus présélectionné, cf. le placeholder « Choisir un
    ingrédient » — la ligne 1.2 ne doit plus laisser croire à un choix par
    défaut), mais dans `data-last-price` de chaque `<option>`, recopié en
    JS une fois l'ingrédient réellement choisi. C'est donc là que la
    virgule française se vérifie désormais."""
    page = seeded_client.client.get("/deliveries/new").text
    valeurs = re.findall(r'data-last-price="([^"]*)"', page)
    assert valeurs, "aucun prix pré-rempli (data-last-price) trouvé sur /deliveries/new"
    for v in valeurs:
        assert "." not in v, f"point décimal encore affiché dans le prix pré-rempli : {v!r}"


# ==========================================================================
# Bouton de fichier natif — « Choose File » / « No file chosen » remplacés.
# ==========================================================================
def test_no_native_file_input_is_left_visible_anywhere():
    """Le bouton et le texte natifs du navigateur suivent sa langue système,
    jamais le `lang=\"fr\"` de la page — aucun moyen de les franciser en CSS.
    Seule option : masquer le vrai `<input>` (accessible, pas supprimé) et le
    déclencher par un `<label>` visible, avec le nom du fichier réécrit en JS
    (cf. app.js)."""
    for gabarit in GABARITS:
        texte = gabarit.read_text()
        for m in re.finditer(r'<input\b[^>]*type="file"[^>]*>', texte):
            assert 'class="sr-only"' in m.group(0), (
                f"input[type=file] non masqué (bouton natif visible) dans {gabarit}"
            )
        if 'type="file"' in texte:
            assert "data-champ-fichier" in texte and "data-nom-fichier" in texte, (
                f"pas de déclencheur habillé pour le fichier natif dans {gabarit}"
            )


# ==========================================================================
# Identité — l'écran de connexion ne doit plus afficher un nom générique.
# ==========================================================================
def test_setup_screen_shows_the_product_name_not_a_generic_placeholder(anonymous_client):
    page = anonymous_client.client.get("/login").text  # redirige vers /setup : pas de compte
    assert "Stock resto" in page
    assert ">Stock<" not in page


def test_dashboard_hero_shows_the_product_name_when_restaurant_name_is_blank(anonymous_client):
    """L'accueil a son propre en-tête (bloc `entete` réécrit pour le héros),
    avec sa propre copie du repli — non touchée par le premier correctif sur
    base.html. Un nom d'établissement vide (`restaurant_name=""`, accepté à
    la création du compte) est le seul chemin qui l'atteint réellement."""
    client = anonymous_client.client
    client.post("/setup", data={"email": "vide@bistrot.fr", "password": "motdepasse123"})
    page = client.get("/").text
    assert "Stock resto" in page
    assert ">Stock<" not in page


def test_manifest_colors_match_the_current_white_background():
    manifest = (BASE_DIR / "app" / "static" / "manifest.webmanifest").read_text()
    assert '"background_color": "#ffffff"' in manifest
    assert '"theme_color": "#ffffff"' in manifest


# ==========================================================================
# Comportement réel du déclencheur de fichier habillé — un test statique ne
# vérifie que le balisage, pas que choisir un fichier met bien à jour le nom
# affiché (app.js). Vrai navigateur requis ; ignoré proprement sinon.
# ==========================================================================
EMAIL, PASSWORD = "chef@bistrot.fr", "motdepasse123"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_choosing_a_file_replaces_the_native_english_placeholder_text():
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    import httpx

    db_dir = tempfile.mkdtemp()
    env = {**os.environ, "RESTAURANT_STOCK_DATABASE_URL": f"sqlite:///{db_dir}/coherence.db"}
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=BASE_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(50):
            try:
                if httpx.get(base + "/healthz", timeout=1).status_code == 200:
                    break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("serveur de test non démarré")

        with httpx.Client(base_url=base, follow_redirects=True) as c:
            c.post("/setup", data={"email": EMAIL, "password": PASSWORD, "restaurant_name": "Test"})

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception:
                fallback = Path("/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
                if not fallback.exists():
                    raise
                browser = p.chromium.launch(executable_path=str(fallback))
            page = browser.new_page()
            page.goto(base + "/login")
            page.fill('input[name="email"]', EMAIL)
            page.fill('input[name="password"]', PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")

            page.goto(base + "/sales/import")
            avant = page.locator("[data-nom-fichier]").inner_text()
            assert avant == "Aucun fichier choisi"

            csv_path = BASE_DIR / "sample_data" / "exemple_export_ventes.csv"
            page.set_input_files('input[type="file"]', str(csv_path))
            apres = page.locator("[data-nom-fichier]").inner_text()
            assert apres == csv_path.name, "le nom du fichier choisi doit remplacer le texte par défaut"

            browser.close()
    finally:
        proc.kill()


# ==========================================================================
# U8 — /orders/{batch_id} (« Suggestions de commande ») : trois défauts
# relevés sur cet écran précis. Valider/Rejeter avaient un poids visuel
# inégal (rouge sur le refus, comme si refuser une suggestion était un
# problème) ; le paragraphe d'explication était un dépôt de trois champs
# bruts au lieu d'une phrase ; et les quantités s'affichaient au gramme
# près (voire à la centaine de grammes) même quand un kilo se lit mieux.
# ==========================================================================
def _u8_ingredient(db, name, current_stock, alert_threshold=None):
    ing = models.Ingredient(
        name=name,
        unit=models.Unit.GRAMME,
        unit_cost=0.02,
        storage_zone=models.StorageZone.SEC,
        current_theoretical_stock=current_stock,
        alert_threshold=alert_threshold,
    )
    db.add(ing)
    db.commit()
    return ing


def _u8_sale(db, ingredient, quantity, days_ago):
    db.add(models.StockMovement(
        ingredient_id=ingredient.id,
        movement_type=models.MovementType.VENTE,
        quantity_delta=-quantity,
        resulting_stock=ingredient.current_theoretical_stock,
        created_at=datetime.utcnow() - timedelta(days=days_ago),
    ))
    db.commit()


def _u8_render_batch(seeded_client):
    """Génère un lot avec deux lignes de suggestion : une qui reste au
    gramme (petites quantités) et une qui doit basculer au kilo (grosses
    quantités), puis renvoie le HTML de /orders/{batch_id}."""
    with seeded_client.session_factory() as db:
        settings_service.update_settings(
            db, safety_days=2, target_days=5, rolling_window_days=7
        )
        petite = _u8_ingredient(db, "Beurre U8", current_stock=728)
        _u8_sale(db, petite, 3290, days_ago=3)  # 3290 / 7 jours = 470 g/jour

        # alert_threshold explicite : pas besoin de ventes pour déclencher
        # la suggestion, la conso. moyenne peut rester à 0.
        _u8_ingredient(db, "Farine U8", current_stock=12672, alert_threshold=20000)

        batch = ordering.generate_suggestions(db)
        batch_id = batch.id

    return seeded_client.client.get(f"/orders/{batch_id}").text


def test_u8_valider_et_rejeter_ont_le_meme_poids_visuel(seeded_client):
    page = _u8_render_batch(seeded_client)
    formulaires = re.findall(
        r'<form[^>]*action="/orders/lines/\d+/decide"[^>]*>.*?</form>', page, re.S
    )
    assert len(formulaires) == 2, "les deux lignes générées doivent proposer un formulaire de décision"
    for formulaire in formulaires:
        boutons = re.findall(r'<button[^>]*>.*?</button>', formulaire, re.S)
        valider = next(b for b in boutons if "Valider cette quantité" in b)
        rejeter = next(b for b in boutons if "Rejeter" in b)

        assert "text-alerte" not in valider
        assert "text-alerte" not in rejeter, (
            "refuser une suggestion de routine ne doit pas être teinté alerte "
            "(rouge = écart/rupture, pas un choix de routine)"
        )

        classe_valider = re.search(r'class="([^"]*)"', valider).group(1)
        classe_rejeter = re.search(r'class="([^"]*)"', rejeter).group(1)
        assert "btn-secondaire" in classe_valider
        assert "btn-secondaire" in classe_rejeter, (
            "Valider et Rejeter doivent partager la même famille de bouton "
            f"(trouvé : {classe_valider!r} vs {classe_rejeter!r})"
        )


def test_u8_explication_est_une_phrase_lisible_pas_un_dump(seeded_client):
    page = _u8_render_batch(seeded_client)

    assert "Stock actuel" not in page
    assert "conso. moyenne" not in page
    assert "seuil" not in page, "le seuil est un détail d'implémentation, pas à afficher ligne par ligne"

    assert "suggérés" in page
    assert "il reste" in page
    assert "vous en consommez" in page

    phrase = re.search(r"1,62 kg suggérés\s*:\s*il reste 728 g,\s*vous en consommez ~470 g/jour", page)
    assert phrase, "la phrase attendue (quantité, puis stock restant, puis conso.) est absente"


def test_u8_quantites_dans_l_unite_la_plus_lisible(seeded_client):
    page = _u8_render_batch(seeded_client)

    # Jamais plus de 2 décimales après la virgule sur cet écran.
    assert not re.search(r",\d{3,}", page), "précision excessive affichée (plus de 2 décimales)"

    # Une grosse quantité en grammes doit basculer au kilo plutôt que de
    # s'afficher au gramme à quatre chiffres.
    assert "12,67 kg" in page, "942,86 g au lieu de 0,94 kg : le stock ne bascule pas au kilo"
    assert "7,33 kg" in page
    assert not re.search(r"12[  ]?672\s*g\b", page), "quantité restée en grammes non convertie"
    assert not re.search(r"7[  ]?328\s*g\b", page), "quantité restée en grammes non convertie"


# ==========================================================================
# Le total « brut » du graphique de tendance (/metrics) n'était accompagné
# d'aucune explication : deux chiffres proches (« 5,27 € » puis
# « (brut 5,77 €) ») sans rien pour dire pourquoi ils diffèrent ni lequel
# retenir. Le brut additionne les écarts en valeur absolue (aucune
# compensation entre un surplus et une perte), le total net les additionne
# avec leur signe.
# ==========================================================================
def test_metrics_brut_figure_is_explained(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    with sessions() as db:
        session = counting.start_count_session(db, counted_by="Test")
        line = session.lines[0]
        counting.confirm_count_line(
            db, line.id, counted_quantity=line.theoretical_quantity - 1
        )
        counting.complete_count_session(db, session.id)

    page = client.get("/metrics").text
    assert "(brut" in page, "le test ne porte plus sur un écran qui affiche encore le brut"
    assert (
        "sans laisser un surplus compenser une perte ailleurs" in page
    ), "aucune explication de ce que mesure le total « brut », par opposition au total net"


# ==========================================================================
# Les grandes quantités en grammes se lisaient mal (« 12 672 g ») sur le
# partiel partagé par /variance et /counting/{id}/summary. `qty_lisible`
# (app/templating.py) bascule en kg au-delà de 1000 g/mL — ici sur le
# partiel directement, comme les tests AC-U6-1 ci-dessus.
# ==========================================================================
def test_variance_table_renders_large_gram_quantities_in_kg():
    lignes = [_ligne("Farine", -1.8, theorique=14400, compte=12672, pct=-12.0)]
    html = _rendu(lignes)
    ancien_theorique = f"{_qty(14400)} g"
    ancien_compte = f"{_qty(12672)} g"

    assert "14,40 kg attendus" in html, "la quantité théorique doit passer en kg au-delà de 1000 g"
    assert "12,67 kg comptés" in html, "la quantité comptée doit passer en kg au-delà de 1000 g"
    assert ancien_compte not in html, "l'ancien affichage en grammes bruts (12 672 g) ne doit plus apparaître"
    assert ancien_theorique not in html, "l'ancien affichage en grammes bruts (14 400 g) ne doit plus apparaître"


# ==========================================================================
# Même défaut que le partiel ci-dessus, mais sur la propre boucle de
# l'accueil (« Derniers écarts ») : elle n'utilise pas variance_table.html
# (cf. commentaire AC-U6-1 dans app/routers/dashboard.py) et n'avait donc
# pas hérité du passage à qty_lisible.
# ==========================================================================
def test_dashboard_derniers_ecarts_renders_large_gram_quantities_in_kg(seeded_client):
    client, sessions = seeded_client.client, seeded_client.session_factory
    with sessions() as db:
        session = counting.start_count_session(db, counted_by="Test")
        farine = next(l for l in session.lines if l.ingredient.name == "Farine")
        counting.confirm_count_line(db, farine.id, counted_quantity=farine.theoretical_quantity - 1200)
        for line in session.lines:
            if line.id != farine.id:
                counting.confirm_count_line(db, line.id, counted_quantity=line.theoretical_quantity)
        counting.complete_count_session(db, session.id)

    page = client.get("/").text
    assert "20 kg attendus" in page, "la quantité théorique doit passer en kg au-delà de 1000 g"
    assert "18,80 kg comptés" in page, "la quantité comptée doit passer en kg au-delà de 1000 g"
    assert "20 000 g" not in page, "ancien affichage brut (théorique) ne doit plus apparaître"
    assert "18 800 g" not in page, "ancien affichage brut (compté) ne doit plus apparaître"
