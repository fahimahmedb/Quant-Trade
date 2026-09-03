"""Direction visuelle V1.2 — révision 2 : cas de test TC-D2-01 à TC-D2-08.

Un test par cas de la section 9 de la révision, à la même exigence que la
suite NR-01→18 : nommé, traçable, et vérifiant le comportement réel plutôt
que la seule présence d'une règle CSS.

Ce fichier ne redouble pas ce qui est déjà vérifié ailleurs :
- TC-D2-02 (contraste du héros) et TC-D2-03 (contraste des pastilles) sont
  dans tests/test_design_tokens.py, avec les autres seuils de contraste.
- TC-D2-07 (NR-01→18 verts) est la suite tests/test_nr.py elle-même ; ce
  fichier vérifie seulement qu'elle est bien complète et qu'aucun cas n'a
  disparu en silence.

Les cas qui demandent une vraie interaction (D2-01, D2-04, D2-05, D2-06)
tournent dans un vrai Chromium — ignorés proprement s'il est absent, la
suite reste exécutable partout.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
WIDTHS = (430, 390, 360, 320)
EMAIL, PASSWORD = "chef@bistrot.fr", "motdepasse123"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _launch_chromium(playwright):
    try:
        return playwright.chromium.launch()
    except Exception:  # navigateur non installé via `playwright install`
        fallback = Path("/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        if fallback.exists():
            return playwright.chromium.launch(executable_path=str(fallback))
        raise


@pytest.fixture(scope="module")
def dashboard_server():
    """Serveur réel avec un comptage terminé en écart : le héros et la liste
    d'écarts ont du contenu réel à afficher, pas un écran vide."""
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    import httpx

    db_dir = tempfile.mkdtemp()
    env = {**os.environ, "RESTAURANT_STOCK_DATABASE_URL": f"sqlite:///{db_dir}/d2.db"}
    subprocess.run([sys.executable, "-m", "app.seed"], cwd=BASE_DIR, env=env, check=True,
                   capture_output=True)
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=BASE_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            if httpx.get(base + "/healthz", timeout=1).status_code == 200:
                break
        except Exception:
            time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail("serveur de test non démarré")

    with httpx.Client(base_url=base, follow_redirects=True) as c:
        c.post("/setup", data={"email": EMAIL, "password": PASSWORD,
                               "restaurant_name": "Bistrot D2"})
        r = c.post("/counting/start", data={"counted_by": "D2"})
        session_id = r.url.path.rstrip("/").split("/")[-1]
        page = c.get(f"/counting/{session_id}").text
        import re

        champs = re.findall(r'name="(count_\d+)"\s+value="([^"]+)"', page)
        # Une vraie ligne en écart : sans elle, TC-D2-04 n'aurait rien à presser
        # dans la liste des écarts.
        for i, (nom, valeur) in enumerate(champs):
            cible = round(float(valeur) * (0.9 if i == 0 else 1.0), 2)
            zone = re.search(rf'action="([^"]*zone/[^"]*)"[^>]*>(?:(?!</form>).)*?name="{nom}"',
                             page, re.S)
            c.post(base + zone.group(1), data={nom: str(cible)})
        c.post(f"/counting/{session_id}/complete")
        c.post("/orders/generate")

    try:
        with sync_playwright() as p:
            browser = _launch_chromium(p)
            yield base, browser
            browser.close()
    finally:
        proc.kill()


def _login(page, base):
    page.goto(base + "/login")
    page.fill('input[name="email"]', EMAIL)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


# ==========================================================================
# TC-D2-01 — accueil à 320/360/390/430 px : aucun débordement, la rangée de
# 4 actions reste sur une seule ligne à toutes les largeurs.
# ==========================================================================


@pytest.mark.parametrize("width", WIDTHS)
def test_tc_d2_01_quick_action_row_stays_on_one_line_at_every_width(dashboard_server, width):
    base, browser = dashboard_server
    page = browser.new_page(viewport={"width": width, "height": 844})
    _login(page, base)
    page.goto(base + "/")
    page.wait_for_load_state("networkidle")

    assert page.evaluate("document.body.scrollWidth") <= width, (
        f"débordement horizontal de l'accueil à {width}px"
    )

    actions = page.locator(".action-rapide")
    assert actions.count() == 4, "quatre actions justifiées, pas plus, pas moins"
    tops = {round(actions.nth(i).bounding_box()["y"]) for i in range(4)}
    assert len(tops) == 1, (
        f"les actions ne sont pas toutes sur la même ligne à {width}px : {tops}"
    )
    page.close()


# ==========================================================================
# TC-D2-04 — appui sur une ligne de liste : changement de fond visible,
# retour à l'état normal au relâchement.
# ==========================================================================


def test_tc_d2_04_pressing_a_list_row_changes_background_and_releases(dashboard_server):
    base, browser = dashboard_server
    page = browser.new_page(viewport={"width": 390, "height": 844})
    _login(page, base)
    page.goto(base + "/")
    page.wait_for_load_state("networkidle")

    ligne = page.locator(".ligne").first
    assert ligne.count() == 1, "au moins une ligne d'écart doit être affichée"
    avant = ligne.evaluate("el => getComputedStyle(el).backgroundColor")

    box = ligne.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    # `getComputedStyle` immédiatement après l'appui lirait l'instant t=0 de
    # la transition (encore la valeur de repos) : une frame doit s'écouler.
    page.wait_for_timeout(80)
    pendant = ligne.evaluate("el => getComputedStyle(el).backgroundColor")
    page.mouse.up()
    page.wait_for_timeout(220)  # au-delà de la durée de transition (140 ms)
    apres = ligne.evaluate("el => getComputedStyle(el).backgroundColor")

    assert pendant != avant, "aucun changement de fond visible à l'appui"
    assert apres == avant, "le fond ne revient pas à l'état normal au relâchement"
    page.close()


# ==========================================================================
# TC-D2-05 — appui sur un bouton rond de la rangée d'actions : effet
# d'enfoncement visible, action déclenchée, cible tactile ≥ 48 px.
# ==========================================================================


def test_tc_d2_05_quick_action_press_effect_navigation_and_touch_target(dashboard_server):
    base, browser = dashboard_server
    page = browser.new_page(viewport={"width": 390, "height": 844})
    _login(page, base)
    page.goto(base + "/")
    page.wait_for_load_state("networkidle")

    compter = page.locator('a.action-rapide[href="/counting"]')
    box = compter.bounding_box()
    assert box["width"] >= 48 and box["height"] >= 48, (
        f"cible tactile de {box['width']}x{box['height']}px, minimum 48x48"
    )

    # L'effet d'enfoncement d'abord : un appui maintenu, relâché après avoir
    # laissé une frame peindre la transition.
    cercle = compter.locator(".action-rapide-cercle")
    repos = cercle.evaluate("el => getComputedStyle(el).transform")
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.wait_for_timeout(80)
    enfonce = cercle.evaluate("el => getComputedStyle(el).transform")
    page.mouse.up()
    assert enfonce != repos, "aucun effet d'enfoncement visible à l'appui"

    # La navigation, séparément et sans ambiguïté : le relâchement précédent
    # a pu ou non déjà déclencher une navigation asynchrone (l'issue exacte
    # d'un appui maintenu artificiellement puis relâché n'est pas garantie à
    # la milliseconde) ; revenir à un état connu avant un clic normal évite
    # toute course entre la navigation en cours et la lecture de l'URL.
    page.goto(base + "/")
    page.wait_for_load_state("networkidle")
    page.click('a.action-rapide[href="/counting"]')
    page.wait_for_load_state("networkidle")
    assert page.url.rstrip("/").endswith("/counting"), (
        f"l'action n'a pas déclenché la navigation attendue : {page.url}"
    )
    page.close()


# ==========================================================================
# TC-D2-06 — préférence système « animations réduites » activée : le retour
# au toucher (déclenché par une action) reste actif ; toute transition non
# déclenchée par l'utilisateur disparaît.
# ==========================================================================


def test_tc_d2_06_touch_feedback_survives_reduced_motion_preference(dashboard_server):
    base, browser = dashboard_server
    context = browser.new_context(viewport={"width": 390, "height": 844},
                                  reduced_motion="reduce")
    page = context.new_page()
    _login(page, base)
    page.goto(base + "/")
    page.wait_for_load_state("networkidle")

    assert page.evaluate(
        "matchMedia('(prefers-reduced-motion: reduce)').matches"
    ), "la préférence n'est pas transmise à la page"

    ligne = page.locator(".ligne").first
    avant = ligne.evaluate("el => getComputedStyle(el).backgroundColor")
    box = ligne.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.wait_for_timeout(80)
    pendant = ligne.evaluate("el => getComputedStyle(el).backgroundColor")
    page.mouse.up()

    assert pendant != avant, (
        "le retour au toucher a disparu avec « animations réduites » : "
        "il doit rester actif, seule la transition doit s'annuler"
    )

    duree_ms = ligne.evaluate("""el => {
      const d = getComputedStyle(el).transitionDuration;
      return d.endsWith('ms') ? parseFloat(d) : parseFloat(d) * 1000;
    }""")
    assert duree_ms <= 0.01, (
        f"la transition n'est pas neutralisée par « animations réduites » : {duree_ms}ms"
    )
    context.close()


# ==========================================================================
# TC-D2-07 — la suite de non-régression complète reste verte. Pas une
# répétition de tests/test_nr.py : une garantie que ses 18 cas existent
# toujours tous, pour qu'une suppression discrète ne passe pas inaperçue.
# ==========================================================================


def test_tc_d2_07_all_eighteen_regression_cases_are_still_collected():
    import subprocess as sp

    result = sp.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         str(BASE_DIR / "tests" / "test_nr.py")],
        capture_output=True, text=True, cwd=BASE_DIR,
    )
    numeros = {
        int(m) for m in __import__("re").findall(r"test_nr(\d\d)", result.stdout)
    }
    attendus = set(range(1, 19)) - {12}  # NR-12 vit dans test_nr_mobile.py
    manquants = attendus - numeros
    assert manquants == set(), f"cas de non-régression disparus : NR-{sorted(manquants)}"


# ==========================================================================
# TC-D2-08 — écran des écarts : présence ou non d'un bloc héros, décision
# explicite, jamais une extrapolation automatique du gabarit de l'accueil.
#
# Ce lot ne redessine que l'accueil (méthode, section 5 : deux écrans témoins
# avant généralisation). /variance n'a donc pas de héros aujourd'hui — ce
# test verrouille cette absence comme un choix, pas un oubli : le jour où
# quelqu'un copie le gabarit du héros sur /variance, ce test échoue et force
# à documenter la décision plutôt qu'à la laisser se produire par copier-coller.
# ==========================================================================


def test_tc_d2_08_variance_screen_hero_presence_is_a_documented_decision_not_yet_made():
    variance = (BASE_DIR / "app" / "templates" / "variance" / "list.html").read_text()
    assert "heros" not in variance, (
        "un bloc héros est apparu sur /variance sans décision documentée — "
        "TC-D2-08 demande un choix explicite (présence ou absence), pas une "
        "extrapolation automatique du gabarit de l'accueil"
    )


# ==========================================================================
# Régression — le héros ne doit jamais retomber sur la progression d'un
# comptage en cours (0/N au départ, lisible comme « 0 conforme »). Trois
# états explicites (app/routers/dashboard.py, `hero_state`), vérifiés ici
# sur le HTML rendu : pas besoin d'un navigateur, c'est un rendu serveur.
# ==========================================================================
from app import models
from app.services import counting


def _complete_a_session_with_known_variance(sessions):
    """Un comptage terminé, avec au moins une ligne en écart : de quoi
    calculer un conform_lines/counted_lines sans ambiguïté."""
    with sessions() as db:
        session = counting.start_count_session(db, counted_by="Test")
        lines = session.lines
        for i, line in enumerate(lines):
            valeur = line.theoretical_quantity * (0.5 if i == 0 else 1.0)
            counting.confirm_count_line(db, line.id, counted_quantity=valeur)
        counting.complete_count_session(db, session.id)
        total = len(lines)
        conformes = total - 1  # une seule ligne mise en écart ci-dessus
    return conformes, total


def test_hero_shows_last_completed_conformity_even_while_a_session_is_open(seeded_client):
    """Le bug exact remonté : un comptage relancé après un premier comptage
    terminé ne doit pas faire retomber le héros à « 0/9 »."""
    client, sessions = seeded_client.client, seeded_client.session_factory
    conformes, total = _complete_a_session_with_known_variance(sessions)

    # Un second comptage démarre, encore vide : c'est lui qui produisait le
    # « 0/9 » trompeur avant correction.
    client.post("/counting/start", data={"counted_by": "Test"})

    page = client.get("/").text
    assert f'<span class="nombre">{conformes}</span><span class="heros-attenue">/{total}</span>' in page, (
        "le héros n'affiche pas la conformité du comptage terminé pendant "
        "qu'un autre est en cours"
    )
    assert f'<span class="nombre">0</span><span class="heros-attenue">/{total}</span>' not in page, (
        "le héros affiche encore la progression (0/N) du comptage en cours"
    )
    assert "Comptage en cours" in page and "reprendre" in page, (
        "le comptage en cours doit rester visible, en élément secondaire"
    )
    assert "ingrédients conformes au dernier comptage" in page


def test_hero_first_ever_session_in_progress_shows_no_misleading_digit(seeded_client):
    """Aucun comptage jamais terminé, mais un premier est en cours : troisième
    état, défini consciemment plutôt qu'un 0/N par défaut."""
    client = seeded_client.client
    client.post("/counting/start", data={"counted_by": "Test"})

    page = client.get("/").text
    assert "Premier comptage en cours" in page
    assert "Comptage en cours" in page and "reprendre" in page
    assert "ingrédients conformes" not in page, (
        "aucune conformité n'existe encore : ce libellé ne doit pas apparaître"
    )
    assert 'class="heros-chiffre"' not in page, (
        "aucun chiffre géant ne doit être affiché sans donnée favorable réelle"
    )


def test_hero_empty_state_has_no_digit_and_no_resume_link(seeded_client):
    """Ni comptage terminé, ni comptage en cours : l'état vide d'origine."""
    page = seeded_client.client.get("/").text
    assert "Aucun comptage effectué pour l'instant" in page
    assert "Comptage en cours" not in page
    assert 'class="heros-chiffre"' not in page
