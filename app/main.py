from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine
from .routes.patients import router as patients_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("[STARTUP] Patient database initialized.", flush=True)
    yield


app = FastAPI(
    title="Voice AI Patient Registration API",
    version="1.0.0",
    description="REST API backing the Voice AI Patient Registration assessment.",
    lifespan=lifespan,
)

app.include_router(patients_router)


@app.get("/health")
def health():
    return {"data": {"status": "ok"}, "error": None}


@app.get("/")
def root():
    return {
        "data": {
            "service": "Voice AI Patient Registration API",
            "docs": "/docs",
            "health": "/health",
        },
        "error": None,
    }
