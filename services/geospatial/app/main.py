from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.api.zones import router as zones_router
from app.config.logging_config import configure_logging


configure_logging()

app = FastAPI(
    title="Geospatial & Zone Aggregation Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://parcial1patronesarquitectonicos.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    zones_router,
    prefix="/v1",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "geospatial",
        "version": "1.0.0",
    }


handler = Mangum(app, lifespan="off")