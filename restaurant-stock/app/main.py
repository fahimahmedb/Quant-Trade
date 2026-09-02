import hashlib
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, UPLOAD_DIR
from app.database import init_db
from app.middleware import ErrorLogMiddleware, RequireLoginMiddleware
from app.routers import (
    auth,
    counting,
    dashboard,
    deliveries,
    ingredients,
    metrics,
    orders,
    recipes,
    sales,
    settings,
    variance,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Gestion de stock — Restaurant indépendant", lifespan=lifespan)

# Fermé par défaut : chaque écran métier exige une session (F2, AC-F2-1).
# Ajouté en premier donc exécuté en dernier : le journal d'erreurs enveloppe
# le contrôle de session et voit aussi ce qui casse à l'intérieur.
app.add_middleware(RequireLoginMiddleware)
app.add_middleware(ErrorLogMiddleware)


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


# Fichiers dont le contenu détermine le comportement hors-ligne : coquille
# mise en cache par le service worker, et gabarits qui fixent la structure
# de la page de comptage que ce même service worker sait rejouer hors-ligne.
_SW_WATCHED_FILES = [
    Path(BASE_DIR) / "app" / "static" / "sw.js",
    Path(BASE_DIR) / "app" / "static" / "offline-count.js",
    Path(BASE_DIR) / "app" / "static" / "app.js",
    Path(BASE_DIR) / "app" / "static" / "app.css",
    Path(BASE_DIR) / "app" / "static" / "tailwind.css",
    Path(BASE_DIR) / "app" / "static" / "manifest.webmanifest",
    *sorted((Path(BASE_DIR) / "app" / "static" / "fonts").glob("*.woff2")),
    Path(BASE_DIR) / "app" / "templates" / "base.html",
    Path(BASE_DIR) / "app" / "templates" / "counting" / "session.html",
]


def _sw_build_version() -> str:
    """Empreinte de tout ce qui détermine ce que le service worker sert.

    Calculée une fois au démarrage du processus : un déploiement redémarre
    toujours le serveur, donc pas besoin de la recalculer à chaque requête.
    Elle remplace une constante à incrémenter à la main — oubliée une fois,
    un téléphone déjà équipé continuerait de servir l'ancien écran de
    comptage depuis son cache sans que personne s'en aperçoive.
    """
    digest = hashlib.sha256()
    for path in _SW_WATCHED_FILES:
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


_SW_SOURCE = (
    (Path(BASE_DIR) / "app" / "static" / "sw.js")
    .read_text()
    .replace('"__BUILD_VERSION__"', f'"{_sw_build_version()}"')
)


@app.get("/sw.js", include_in_schema=False)
def service_worker():
    """Servi à la racine : un service worker ne contrôle que son propre
    chemin et en dessous. Depuis /static/, il ne verrait pas /counting."""
    return Response(
        _SW_SOURCE,
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"},
    )

app.mount("/static", StaticFiles(directory=str(Path(BASE_DIR) / "app" / "static")), name="static")

# Photos de bons de livraison (F1) : servies depuis les données du restaurant,
# jamais depuis le dépôt.
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(deliveries.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(sales.router)
app.include_router(counting.router)
app.include_router(variance.router)
app.include_router(orders.router)
app.include_router(metrics.router)
app.include_router(settings.router)
