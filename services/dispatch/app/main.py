from fastapi import FastAPI
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

from app.api.dispatches import router as dispatch_router
from app.config.logging_config import configure_logging


configure_logging()


app = FastAPI(
    title="Dispatch & Resource Assignment Service",
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
    dispatch_router,
    prefix="/v1",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "dispatch",
        "version": "1.0.0",
    }


handler = Mangum(
    app,
    lifespan="off",
)