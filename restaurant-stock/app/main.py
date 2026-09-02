from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, UPLOAD_DIR
from app.database import init_db
from app.routers import (
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

app.mount("/static", StaticFiles(directory=str(Path(BASE_DIR) / "app" / "static")), name="static")

# Photos de bons de livraison (F1) : servies depuis les données du restaurant,
# jamais depuis le dépôt.
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

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
