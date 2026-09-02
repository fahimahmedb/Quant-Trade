from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
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
