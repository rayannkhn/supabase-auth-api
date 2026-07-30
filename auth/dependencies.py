from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.supabase_client import supabase

# Shared security scheme: this is what makes FastAPI show the padlock icon
# and the "Authorize" button in /docs for every route that depends on it.
# auto_error=False so a missing/malformed header falls through to our own
# 401 body below instead of FastAPI's default 403.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """The single place that verifies a Supabase access token.

    Every protected route depends on this function (directly, or indirectly
    through another dependency) instead of re-parsing the Authorization
    header or calling supabase.auth.get_user() itself.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail={"error": "Access token required"})

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

    user = getattr(response, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

    return user
