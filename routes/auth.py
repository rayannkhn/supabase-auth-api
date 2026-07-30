from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from auth.dependencies import bearer_scheme, get_current_user
from core.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    # Optional so a missing field yields our own 400, not FastAPI's 422.
    email: Optional[str] = None
    password: Optional[str] = None


@router.post("/signup", status_code=201)
async def signup(payload: Credentials):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail={"error": "email and password are required"})

    try:
        response = supabase.auth.sign_up(
            {"email": payload.email, "password": payload.password}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

    return response.user


@router.post("/login")
async def login(payload: Credentials):
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail={"error": "email and password are required"})

    try:
        response = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid login credentials"})

    if not response.session:
        raise HTTPException(status_code=401, detail={"error": "Invalid login credentials"})

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
    }


@router.post("/logout", status_code=204)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    _user=Depends(get_current_user),
):
    # _user enforces that this route is only reachable with a verified
    # token (via the shared get_current_user dependency). We separately
    # depend on bearer_scheme to get the raw token string for sign_out --
    # FastAPI caches dependency results per-request, so this does not
    # re-parse the header or duplicate any verification logic.
    #
    # supabase.auth.sign_out() (no args) only signs out whatever session is
    # cached inside this client instance -- meaningless here since one
    # global client serves every user. supabase.auth.admin.sign_out(jwt) is
    # the SDK's own documented way to revoke an arbitrary caller-supplied
    # token, which requires the client to be built with the service_role
    # key (see core/supabase_client.py).
    supabase.auth.admin.sign_out(credentials.credentials)
    return Response(status_code=204)
