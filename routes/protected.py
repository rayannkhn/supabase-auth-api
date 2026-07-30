from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from core.supabase_client import supabase

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/profile")
async def profile(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        return JSONResponse(status_code=401, content={"error": "Access token required"})

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        return JSONResponse(status_code=401, content={"error": "Access token required"})

    token = parts[1].strip()

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

    user = getattr(response, "user", None)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }
