from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/profile")
async def profile(request: Request):
    # Not yet verified against Supabase (that's Stage 3) -- for now this
    # only checks that a well-formed bearer token was even sent.
    authorization = request.headers.get("Authorization")
    if not authorization:
        return JSONResponse(status_code=401, content={"error": "Access token required"})

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        return JSONResponse(status_code=401, content={"error": "Access token required"})

    # TODO (Stage 3): actually call supabase.auth.get_user(token) here.
    return {"message": "token received, not yet verified"}
