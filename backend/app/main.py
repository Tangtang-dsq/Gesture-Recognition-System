from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.rest import router as rest_router
from app.api.ws import router as ws_router
from app.core.config import settings
from app.core.db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Gesture Recognition System", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(rest_router, prefix="/api")
    app.include_router(ws_router)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
