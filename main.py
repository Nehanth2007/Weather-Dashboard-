from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import weather
from app.core.config import settings
from app.core.cache import init_cache, close_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_cache()
    yield
    await close_cache()


app = FastAPI(
    title="Weather Dashboard API",
    description="A weather aggregation API with Redis caching and 5-day forecasts.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(weather.router, prefix="/weather", tags=["Weather"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "message": "Weather Dashboard API is running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
