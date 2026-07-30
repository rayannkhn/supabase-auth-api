from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
