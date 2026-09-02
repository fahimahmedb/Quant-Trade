"""NR-12 — 14 écrans sans débordement horizontal à 320/360/390 px.

A besoin d'un vrai Chromium (Playwright). Ignoré proprement si absent, pour
que la suite reste exécutable partout ; la CI installe Chromium.
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
# AC-D-5 : la barre d'onglets ne doit se couper à aucune largeur usuelle.
# 430 px est le plus grand téléphone courant, 320 px le plus petit.
WIDTHS = (430, 390, 360, 320)


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
def live_server():
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    db_dir = tempfile.mkdtemp()
    env = {**os.environ, "RESTAURANT_STOCK_DATABASE_URL": f"sqlite:///{db_dir}/nr12.db"}
    subprocess.run([sys.executable, "-m", "app.seed"], cwd=BASE_DIR, env=env, check=True,
                   capture_output=True)
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=BASE_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    import httpx

    for _ in range(50):
        try:
            if httpx.get(base + "/healthz", timeout=1).status_code == 200:
                break
        except Exception:
            time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail("serveur de test non démarré")

    # Données pour que chaque écran ait du contenu : import, comptage terminé, suggestions.
    with httpx.Client(base_url=base, follow_redirects=True) as c:
        c.post("/setup", data={"email": "chef@bistrot.fr", "password": "motdepasse123",
                               "restaurant_name": "Bistrot NR-12"})
        csv_path = BASE_DIR / "sample_data" / "exemple_export_ventes.csv"
        c.post("/sales/import", files={"file": (csv_path.name, csv_path.read_bytes(), "text/csv")})
        r = c.post("/counting/start", data={"counted_by": "NR-12"})
        session_id = r.url.path.rstrip("/").split("/")[-1]
        c.post(f"/counting/{session_id}/complete")
        c.post("/orders/generate")
        c.post("/deliveries/new", data={
            "received_on": "2026-09-01", "supplier": "Metro", "note": "",
            "ingredient_id": ["1", "2"], "quantity": ["25000", "24"],
            "unit_price": ["1,40", "0,38"],
        })
        c.post("/counting/start", data={"counted_by": "NR-12 (en cours)"})

    try:
        with sync_playwright() as p:
            browser = _launch_chromium(p)
            yield base, browser, session_id
            browser.close()
    finally:
        proc.kill()


SCREENS = [
    "/login",
    "/", "/ingredients", "/ingredients/new", "/ingredients/1/edit",
    "/recipes", "/recipes/new", "/recipes/1/edit",
    "/sales/import", "/sales/imports/1",
    "/counting", "/counting/{open}", "/counting/{done}/summary",
    "/deliveries", "/deliveries/new", "/deliveries/1",
    "/variance", "/orders", "/metrics", "/settings",
]


@pytest.mark.parametrize("width", WIDTHS)
def test_nr12_no_horizontal_overflow_on_every_screen(live_server, width):
    base, browser, done_session = live_server
    page = browser.new_page(viewport={"width": width, "height": 844})
    # Les écrans sont protégés (F2) : on se connecte avant de les parcourir.
    page.goto(base + "/login")
    page.fill('input[name="email"]', "chef@bistrot.fr")
    page.fill('input[name="password"]', "motdepasse123")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    # id de la session ouverte = dernière créée
    open_session = str(int(done_session) + 1)
    overflowing = []
    for screen in SCREENS:
        path = screen.replace("{open}", open_session).replace("{done}", done_session)
        page.goto(base + path)
        page.wait_for_load_state("networkidle")
        assert page.url.startswith(base), path
        scroll_width = page.evaluate("document.body.scrollWidth")
        if scroll_width > width:
            overflowing.append(f"{path} ({scroll_width}px > {width}px)")
    page.close()
    assert overflowing == [], overflowing


@pytest.mark.parametrize("width", WIDTHS)
def test_ac_d_5_bottom_tab_bar_never_overflows_or_clips(live_server, width):
    """La navigation était coupée à 390 px dans la première direction.

    Les cinq onglets se partagent la largeur à parts égales, donc aucun n'a de
    largeur propre à faire déborder : on vérifie que la barre tient dans la
    fenêtre et qu'aucun onglet ne dépasse de son rail.
    """
    base, browser, _done = live_server
    page = browser.new_page(viewport={"width": width, "height": 844})
    page.goto(base + "/login")
    page.fill('input[name="email"]', "chef@bistrot.fr")
    page.fill('input[name="password"]', "motdepasse123")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")

    rail = page.locator(".barre-onglets-rail")
    assert rail.count() == 1, "la barre d'onglets doit être présente"
    boite = rail.bounding_box()
    assert boite["width"] <= width, f"rail de {boite['width']}px dans {width}px"

    onglets = page.locator(".onglet")
    assert onglets.count() == 5, "quatre onglets plus « Plus »"
    for i in range(onglets.count()):
        onglet = onglets.nth(i).bounding_box()
        assert onglet["x"] >= -0.5, f"onglet {i} sort à gauche à {width}px"
        assert onglet["x"] + onglet["width"] <= width + 0.5, (
            f"onglet {i} sort à droite à {width}px"
        )
        # AC-D-4 : la cuisine gagne sur l'élégance, cible d'au moins 48 px.
        assert onglet["height"] >= 48, f"onglet {i} haut de {onglet['height']}px"
    page.close()
