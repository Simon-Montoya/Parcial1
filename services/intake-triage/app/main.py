from fastapi import FastAPI

from app.api.emergencies import router as emergencies_router


app = FastAPI(
    title="Emergency Intake & Triage Service",
    version="1.0.0"
)

app.include_router(
    emergencies_router,
    prefix="/v1"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "intake-triage"
    }
