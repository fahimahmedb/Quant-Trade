"""F3 — comptage hors-ligne, vérifié dans un vrai navigateur.

Les tests serveur (test_offline_counting.py) prouvent le contrat de la file.
Celui-ci prouve ce qu'aucun test serveur ne peut prouver : que la page reste
affichable sans réseau, que la saisie survit à la fermeture de l'onglet, et
qu'elle repart toute seule au retour du réseau.

A besoin d'un vrai Chromium (Playwright). Ignoré proprement s'il est absent.
"""
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
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
def offline_server():
    """Serveur réel + Chromium. `127.0.0.1` est une origine sûre : le service
    worker s'y enregistre sans HTTPS."""
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    import httpx

    db_dir = tempfile.mkdtemp()
    env = {**os.environ, "RESTAURANT_STOCK_DATABASE_URL": f"sqlite:///{db_dir}/f3.db"}
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
                               "restaurant_name": "Bistrot F3"})

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


def _session_id(url: str) -> str:
    """Identifiant de session dans l'URL, sans la chaîne de requête du flash."""
    match = re.search(r"/counting/(\d+)", url)
    assert match, url
    return match.group(1)


def _start_count(page, base) -> str:
    """Démarre un comptage neuf, en clôturant d'abord celui resté ouvert.

    L'accueil masque le formulaire de démarrage tant qu'une session court :
    sans cette clôture, le deuxième test hériterait des lignes du premier.
    """
    page.goto(base + "/counting")
    running = page.locator('a[href^="/counting/"]:has-text("Continuer")')
    if running.count():
        page.request.post(f"{base}/counting/{_session_id(running.first.get_attribute('href'))}/complete")
        page.goto(base + "/counting")
    page.click('form[action="/counting/start"] button[type="submit"]')
    page.wait_for_load_state("networkidle")
    return _session_id(page.url)


def _install_service_worker(page, base, session_id):
    """Charge la page puis attend que le service worker la contrôle.

    Un service worker ne prend la main qu'après activation : sans ce
    rechargement, la page suivante viendrait encore du réseau et le test
    hors-ligne ne prouverait rien.
    """
    page.goto(f"{base}/counting/{session_id}")
    page.evaluate("navigator.serviceWorker.ready")  # attend l'activation
    page.reload()
    page.wait_for_load_state("networkidle")
    page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=10_000)


def test_counting_page_survives_a_network_cut_and_syncs_on_reconnect(offline_server):
    """TC-F3-01/02/04 côté navigateur : coupure, onglet fermé, retour du réseau."""
    import httpx

    base, browser = offline_server
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    _login(page, base)
    session_id = _start_count(page, base)
    _install_service_worker(page, base, session_id)

    line_ids = page.eval_on_selector_all(
        "[data-count-row] .count-input", "els => els.map(e => e.name.replace('count_',''))"
    )
    assert len(line_ids) == 9, line_ids

    # --- Coupure réseau au milieu du comptage -------------------------------
    context.set_offline(True)
    page.reload()
    page.wait_for_load_state("domcontentloaded")
    assert "Comptage" in page.title(), "page de comptage indisponible hors-ligne"
    assert page.eval_on_selector_all("[data-count-row]", "els => els.length") == 9

    banner = page.locator("[data-offline-banner]")
    assert banner.is_visible(), "aucun avertissement hors-ligne"
    assert "Hors ligne" in banner.inner_text()

    # Saisie de 5 lignes hors-ligne, puis enregistrement de la zone.
    zone = page.locator("form[data-zone-form]").first
    inputs = zone.locator(".count-input")
    entered = inputs.count()
    for i in range(entered):
        inputs.nth(i).fill(str(100 + i))
    zone.locator('button[type="submit"]').click()
    page.wait_for_timeout(300)

    assert page.url.split("?")[0].endswith(f"/counting/{session_id}"), \
        "la page ne doit pas être quittée hors-ligne"
    queued = page.evaluate(
        f"JSON.parse(localStorage.getItem('comptage-file-{session_id}') || '[]').length"
    )
    assert queued == entered, f"{queued} ligne(s) en file, {entered} attendues"
    assert "en attente" in banner.inner_text()

    # --- Onglet fermé hors-ligne, puis rouvert (TC-F3-02) -------------------
    page.close()
    page = context.new_page()
    page.goto(f"{base}/counting/{session_id}")
    page.wait_for_load_state("domcontentloaded")
    recovered = page.evaluate(
        f"JSON.parse(localStorage.getItem('comptage-file-{session_id}') || '[]').length"
    )
    assert recovered == entered, "brouillon perdu à la réouverture de l'onglet"
    banner = page.locator("[data-offline-banner]")
    assert "en attente" in banner.inner_text()

    # --- Retour du réseau : la file part toute seule ------------------------
    context.set_offline(False)
    page.wait_for_function(
        f"JSON.parse(localStorage.getItem('comptage-file-{session_id}') || '[]').length === 0",
        timeout=15_000,
    )
    page.wait_for_timeout(300)
    assert "synchronisé" in banner.inner_text(), banner.inner_text()

    # Vérification côté serveur : ce qu'un autre appareil verrait maintenant.
    with httpx.Client(base_url=base, follow_redirects=True) as c:
        c.post("/login", data={"email": EMAIL, "password": PASSWORD, "next": "/"})
        html = c.get(f"/counting/{session_id}").text
    stored = {float(v) for v in re.findall(r'name="count_\d+"\s+value="([^"]+)"', html)}
    for i in range(entered):
        assert float(100 + i) in stored, f"ligne {100 + i} absente du serveur : {sorted(stored)}"

    context.close()


def test_second_device_conflict_is_shown_not_silently_merged(offline_server):
    """TC-F3-03 côté navigateur : la saisie écrasée est nommée à l'écran."""
    import httpx

    base, browser = offline_server
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    _login(page, base)
    session_id = _start_count(page, base)
    _install_service_worker(page, base, session_id)

    line_id = page.eval_on_selector(
        "[data-count-row] .count-input", "el => el.name.replace('count_','')"
    )

    # Le téléphone passe hors-ligne et saisit la ligne.
    context.set_offline(True)
    zone = page.locator("form[data-zone-form]").first
    zone.locator(".count-input").first.fill("11")
    zone.locator('button[type="submit"]').click()
    page.wait_for_timeout(300)

    # Pendant ce temps, un autre appareil saisit la même ligne, plus tard.
    with httpx.Client(base_url=base, follow_redirects=True) as c:
        c.post("/login", data={"email": EMAIL, "password": PASSWORD, "next": "/"})
        response = c.post(f"/counting/{session_id}/sync", json={"entries": [
            {"line_id": int(line_id), "counted_quantity": 22.0},
        ]})
        assert response.json()["applied"] == 1

    context.set_offline(False)
    page.wait_for_function(
        f"JSON.parse(localStorage.getItem('comptage-file-{session_id}') || '[]').length === 0",
        timeout=15_000,
    )
    page.wait_for_timeout(300)

    text = page.locator("[data-offline-banner]").inner_text()
    assert "autre appareil" in text, text
    assert "22" in text, "la valeur conservée doit être affichée"
    context.close()


def test_logout_purges_cached_counting_pages(offline_server):
    """Le téléphone de la cuisine est partagé : après déconnexion, la liste de
    stock ne doit pas rester lisible hors-ligne dans le cache."""
    base, browser = offline_server
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    _login(page, base)
    session_id = _start_count(page, base)
    _install_service_worker(page, base, session_id)

    cached = page.evaluate(
        "caches.keys().then(keys => keys.filter(k => k.startsWith('pages-')))"
    )
    assert cached, "la page de comptage doit être en cache avant le test"

    page.click('form[action="/logout"] button[type="submit"]')
    page.wait_for_load_state("networkidle")

    # `wait_for_function` juge la vérité d'une promesse, toujours vraie :
    # on interroge donc le cache par `evaluate`, qui en attend le résultat.
    remaining = cached
    deadline = time.time() + 10
    while remaining and time.time() < deadline:
        remaining = page.evaluate(
            "caches.keys().then(keys => keys.filter(k => k.startsWith('pages-')))"
        )
        page.wait_for_timeout(200)

    assert remaining == [], f"pages de comptage encore en cache après déconnexion : {remaining}"
    context.close()
