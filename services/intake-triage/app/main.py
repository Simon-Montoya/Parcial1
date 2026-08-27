from fastapi import FastAPI
from mangum import Mangum

from app.api.emergencies import router as emergencies_router
from app.config.logging_config import configure_logging


configure_logging()


app = FastAPI(
    title="Emergency Intake & Triage Service",
    description=(
        "Microservice responsible for emergency intake, "
        "payload validation and deterministic triage."
    ),
    version="1.0.0",
)


app.include_router(
    emergencies_router,
    prefix="/v1",
    tags=["Emergencies"],
)


@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {
        "status": "ok",
        "service": "intake-triage",
        "version": "1.0.0",
    }


handler = Mangum(
    app,
    lifespan="off",
)