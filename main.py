import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

import core.supabase_client  # noqa: F401  (initializes the client at import time)
from routes import auth as auth_routes
from routes import protected as protected_routes
from routes import public as public_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supabase_auth_api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Server running and connected to Supabase")
    yield


app = FastAPI(title="Supabase Auth API", lifespan=lifespan)

app.include_router(public_routes.router)
app.include_router(auth_routes.router)
app.include_router(protected_routes.router)


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
