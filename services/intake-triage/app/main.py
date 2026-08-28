from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.api.emergencies import router as emergencies_router
from app.config.logging_config import configure_logging


configure_logging()

app = FastAPI(
    title="Intake & Triage Service",
    version="1.1.0",
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
    emergencies_router,
    prefix="/v1",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "intake-triage",
        "version": "1.0.0",
    }


handler = Mangum(app, lifespan="off")