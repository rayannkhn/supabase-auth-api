import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

import core.supabase_client  # noqa: F401  (initializes the client at import time)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supabase_auth_api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Server running and connected to Supabase")
    yield


app = FastAPI(title="Supabase Auth API", lifespan=lifespan)


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
