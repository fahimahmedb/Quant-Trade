from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.database import init_db
from app.routers import (
    counting,
    dashboard,
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

app.include_router(dashboard.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(sales.router)
app.include_router(counting.router)
app.include_router(variance.router)
app.include_router(orders.router)
app.include_router(metrics.router)
app.include_router(settings.router)
